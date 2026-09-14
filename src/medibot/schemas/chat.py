"""Pydantic schemas for the chat API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatMessageIn(BaseModel):
    """An inbound chat message (typically the user's prompt)."""

    role: str = Field(default="user", pattern="^(user|assistant)$")
    content: str


class SourceDoc(BaseModel):
    """A retrieved source document citation."""

    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatMessageOut(BaseModel):
    """An outbound chat message for the UI."""

    role: str
    content: str
    sources: list[SourceDoc] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Payload for the chat streaming endpoint."""

    session_id: int | None = None
    message: str
    history: list[ChatMessageIn] = Field(default_factory=list)


class ChatStreamEvent(BaseModel):
    """An SSE event emitted by the chat streaming endpoint."""

    type: str = Field(description="token | sources | done | error")
    content: str = ""
    provider: str | None = None
    sources: list[SourceDoc] = Field(default_factory=list)
