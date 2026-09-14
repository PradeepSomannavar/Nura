"""Rolling conversation summarizer (hybrid memory, Phase 4).

Compresses older evicted turns into a compact clinical summary using the
Phase-2 provider router (Gemini primary → Groq fallback).  Existing summaries
are merged with new turns to keep the summary bounded while preserving
clinical continuity.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from medibot.prompts.memory import ROLLING_SUMMARY_SYSTEM, SUMMARY_SYSTEM_PREFIX
from medibot.services.llm import get_llm

logger = logging.getLogger(__name__)


def _format_turns(messages: Iterable[object]) -> str:
    """Render a list of role/content messages into plain text turns."""
    lines: list[str] = []
    for msg in messages:
        role = getattr(msg, "role", "unknown")
        content = getattr(msg, "content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def summarize_conversation(
    existing_summary: str,
    new_messages: Iterable[object],
) -> str:
    """Merge ``new_messages`` into ``existing_summary`` and return a summary.

    Uses the provider router; on total provider failure returns the existing
    summary unchanged rather than raising.
    """
    turns = _format_turns(new_messages)
    if not turns.strip():
        return existing_summary

    user_text = f"PRIOR SUMMARY:\n{existing_summary or '(none)'}\n\n" \
                f"NEW CONVERSATION TURNS:\n{turns}\n\n" \
                "Produce the updated summary text."

    prompt = [SystemMessage(content=ROLLING_SUMMARY_SYSTEM), HumanMessage(content=user_text)]

    try:
        response = get_llm().invoke(prompt)
        summary = (response.content or "").strip()
        if summary:
            return summary
    except Exception as exc:  # noqa: BLE001 - degrade gracefully to prior summary
        logger.warning("Summary generation failed: %s", exc)

    return existing_summary


def format_summary_messages(summary: str) -> list[BaseMessage]:
    """Build the SystemMessage to inject the rolling summary into the prompt.

    Returns an empty list when there is nothing to inject.
    """
    if not summary:
        return []
    return [SystemMessage(content=f"{SUMMARY_SYSTEM_PREFIX}{summary}")]
