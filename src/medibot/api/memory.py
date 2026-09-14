"""Conversation memory read/write endpoints.

Phase 1 exposes a thin read/write interface over chat sessions.  The full
hybrid memory (buffer + summary) plumbing lands in Phase 4, but the
endpoints and persistence are scaffolded here so the API surface is stable.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from medibot.core.database import get_db
from medibot.models.memory import ChatMessage, ChatSession

router = APIRouter(prefix="/api", tags=["memory"])


@router.post("/sessions")
def create_session(db: Session = Depends(get_db)) -> dict:
    """Create a new chat session and return its id."""
    session = ChatSession(title="New conversation")
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id}


@router.get("/sessions/{session_id}/messages")
def list_messages(session_id: int, db: Session = Depends(get_db)) -> list[dict]:
    """Return all messages for a session, oldest first."""
    session = db.get(ChatSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    return [
        {"id": m.id, "role": m.role, "content": m.content, "sources": m.sources}
        for m in rows
    ]
