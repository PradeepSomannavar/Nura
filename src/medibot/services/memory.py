"""Hybrid memory: recent-turn buffer + persisted rolling summary.

Keeps the last ``buffer_turns`` (default 5) turns as a raw buffer for the RAG
prompt, and compresses older evicted turns into a rolling clinical summary
persisted to SQLite.  The summary and buffer are both restored from the DB keyed
on ``session_id``, so conversation context survives page refreshes while token
cost stays bounded.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy import select
from sqlalchemy.orm import Session

from medibot.core.config import settings
from medibot.core.database import SessionLocal
from medibot.models.memory import ChatMessage, ConversationSummary
from medibot.services.summarizer import format_summary_messages, summarize_conversation

logger = logging.getLogger(__name__)

#: Extra padding so a single oversized turn isn't truncated mid-pair.
_BUFFER_PAD = 0


@dataclass
class MemoryContext:
    """The memory context assembled for a single chat turn."""

    buffer: list[BaseMessage] = field(default_factory=list)
    summary: str = ""

    def history_messages(self) -> list[BaseMessage]:
        """Summary (if any) prepended to the recent buffer for the RAG prompt."""
        return [*format_summary_messages(self.summary), *self.buffer]


class HybridMemory:
    """Session-scoped conversation memory (buffer + rolling summary)."""

    def __init__(
        self,
        session_id: int | None = None,
        db: Session | None = None,
        buffer_turns: int | None = None,
    ) -> None:
        self.session_id = session_id
        self.db = db or SessionLocal()
        self.buffer_turns = buffer_turns or settings.MEMORY_BUFFER_TURNS
        self.buffer_max = self.buffer_turns * 2
        self._buffer: list[dict[str, str]] = []
        self.summary = ""

        if session_id is not None:
            self._load_from_db()

    # ---------- internal persistence helpers ----------

    def _load_from_db(self) -> None:
        """Restore the rolling summary (buffer is reloaded on demand)."""
        try:
            summary_row = self.db.execute(
                select(ConversationSummary)
                .where(ConversationSummary.session_id == self.session_id)
                .order_by(ConversationSummary.updated_at.desc())
            ).scalars().first()
            if summary_row is not None:
                self.summary = summary_row.summary or ""
        except Exception as exc:  # noqa: BLE001 - persistence must not break chat
            logger.warning("Could not load summary: %s", exc)

    def load_messages(self, history: list[BaseMessage]) -> None:
        """Adopt the provided recent history as the current raw buffer."""
        turns = []
        for msg in history:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            content = msg.content if isinstance(msg.content, str) else ""
            turns.append({"role": role, "content": content})
        self._buffer = turns

    # ---------- public API ----------

    def build_context(self, history: list[BaseMessage], summary: str = "") -> MemoryContext:
        """Keep only the most recent ``buffer_turns`` turns from history."""
        if summary:
            self.summary = summary
        # Derive the summary from the DB if not supplied and a session is set.
        self.load_messages(history)
        end = len(self._buffer)
        start_ix = max(0, end - self.buffer_max)
        recent = self._buffer[start_ix:end]
        messages = self._to_langchain(recent)
        return MemoryContext(buffer=messages, summary=self.summary)

    def should_summarize(self, message_count: int) -> bool:
        """Return True when old messages should be evicted into a summary."""
        return message_count > self.buffer_max

    def evict_and_summarize(self) -> None:
        """Compress the oldest buffered turns into the rolling summary.

        Once the buffer exceeds its maximum, evict the oldest messages (in whole
        turn pairs) needed to bring it back to capacity, merging them into the
        existing persisted summary.
        """
        overflow = len(self._buffer) - self.buffer_max
        if overflow <= 0:
            return
        # Round up to an even count of whole messages so user/assistant pairs
        # stay intact, without evicting more messages than necessary.
        turns_to_evict = (overflow + 1) // 2 * 2
        evicted = self._buffer[:turns_to_evict]
        self._buffer = self._buffer[turns_to_evict:]

        new_summary = summarize_conversation(self.summary, _as_messages(evicted))
        if new_summary != self.summary:
            self.summary = new_summary
            self._save_summary(new_summary)

    def add_message(self, role: str, content: str) -> None:
        """Append a message to the buffer and persist it to the DB."""
        self._buffer.append({"role": role, "content": content})
        if self.session_id is not None:
            self._save_message(role, content)

    def history_messages(self, buffer: list[BaseMessage] | None = None) -> list[BaseMessage]:
        """Summary (if any) prepended to the supplied default buffer."""
        return format_summary_messages(self.summary) + list(buffer or [])

    # ---------- formatting ----------

    @staticmethod
    def _to_langchain(turns: list[dict[str, str]]) -> list[BaseMessage]:
        messages: list[BaseMessage] = []
        for turn in turns:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
        return messages

    def _save_message(self, role: str, content: str) -> None:
        if self.session_id is None:
            return
        try:
            self.db.add(ChatMessage(session_id=self.session_id, role=role, content=content))
            self.db.commit()
        except Exception as exc:  # noqa: BLE001 - persistence must not break chat
            logger.warning("Could not persist message: %s", exc)
            self.db.rollback()

    def _save_summary(self, text: str) -> None:
        if self.session_id is None:
            return
        try:
            row = self.db.execute(
                select(ConversationSummary)
                .where(ConversationSummary.session_id == self.session_id)
            ).scalars().first()
            if row is None:
                self.db.add(ConversationSummary(session_id=self.session_id, summary=text))
            else:
                row.summary = text
                row.version = (row.version or 1) + 1
            self.db.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not persist summary: %s", exc)
            self.db.rollback()

    def close(self) -> None:
        """Close the underlying database session (safe to call once)."""
        try:
            self.db.close()
        except Exception:  # noqa: BLE001
            pass


def _as_messages(turns: list[dict[str, str]]) -> list[BaseMessage]:
    """Convert raw turns back to LangChain messages for the summarizer."""
    return HybridMemory._to_langchain(turns)
