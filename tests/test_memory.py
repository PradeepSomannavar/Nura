"""Tests for the hybrid memory system (buffer + rolling summary, Phase 4)."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy import select

from medibot.core.database import Base, SessionLocal, engine
from medibot.models.memory import ConversationSummary
from medibot.services import memory
from medibot.services.memory import HybridMemory


def _msgs(*contents: tuple[str, str]) -> list:
    """Build LangChain messages from (role, content) pairs."""
    out = []
    for role, content in contents:
        out.append(HumanMessage(content=content) if role == "user" else AIMessage(content=content))
    return out


def test_should_summarize_threshold():
    """Memory flags summarization only once the buffer max is exceeded."""
    mem = HybridMemory(buffer_turns=5)  # buffer_max = 10
    assert mem.should_summarize(10) is False
    assert mem.should_summarize(11) is True


def test_build_context_truncates_to_buffer_max():
    """build_context keeps only the most recent buffer_turns of messages."""
    mem = HybridMemory(buffer_turns=2)  # buffer_max = 4
    history = _msgs(
        ("user", "u1"), ("assistant", "a1"),
        ("user", "u2"), ("assistant", "a2"),
        ("user", "u3"), ("assistant", "a3"),
    )
    ctx = mem.build_context(history)
    # Only the last 4 of 6 messages remain.
    assert [m.content for m in ctx.buffer] == ["u2", "a2", "u3", "a3"]


def test_build_context_keeps_summary_prefix():
    """A summary is prepended as a SystemMessage to the raw buffer."""
    mem = HybridMemory(buffer_turns=2)
    history = _msgs(("user", "u1"), ("assistant", "a1"))
    ctx = mem.build_context(history, summary="Prior clinical context")
    combined = ctx.history_messages()
    assert combined[0].type == "system"
    assert "Prior clinical context" in combined[0].content
    assert [m.content for m in combined[1:]] == ["u1", "a1"]


def test_evict_and_summarize_rolls_oldest_into_summary(monkeypatch):
    """Oldest turns are evicted into a merged summary when the buffer overflows."""
    captured: dict[str, object] = {}

    def fake_summarize(existing, new_messages):
        captured["existing"] = existing
        captured["count"] = len(list(new_messages))
        return "NARRATIVE: " + (existing or "start")

    monkeypatch.setattr(memory, "summarize_conversation", fake_summarize)

    mem = HybridMemory(buffer_turns=2)  # buffer_max = 4
    for i in range(1, 8):
        mem.add_message("user", f"q{i}")
        mem.add_message("assistant", f"a{i}")

    mem.evict_and_summarize()

    # 7 turns (14 messages) exceed capacity (4); the 10 oldest are evicted
    # into a merged summary, leaving only the 4 most recent in the buffer.
    assert captured["count"] == 10
    assert captured["existing"] == ""
    assert len(mem._buffer) == 4
    assert mem._buffer[-1]["content"] == "a7"
    assert mem.summary == "NARRATIVE: start"


def test_summary_persistence_roundtrip():
    """Summary is persisted to and reloaded from SQLite for a session."""
    Base.metadata.create_all(bind=engine)
    session_id = 9000 + int(__import__("time").time()) % 100000
    db = SessionLocal()
    try:
        mem = HybridMemory(session_id=session_id, db=db, buffer_turns=2)
        mem.summary = "Persisted clinical summary"
        mem._save_summary(mem.summary)

        reloaded = HybridMemory(session_id=session_id, db=db, buffer_turns=2)
        assert reloaded.summary == "Persisted clinical summary"

        row = db.execute(
            select(ConversationSummary).where(ConversationSummary.session_id == session_id)
        ).scalars().first()
        assert row is not None
        assert row.summary == "Persisted clinical summary"
        db.delete(row)
        db.commit()
    finally:
        db.close()
