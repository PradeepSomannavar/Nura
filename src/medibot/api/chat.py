"""Chat streaming endpoint (Server-Sent Events)."""

from __future__ import annotations

from collections.abc import Iterator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from medibot.schemas.chat import ChatRequest, ChatStreamEvent
from medibot.services.chat import answer_stream

router = APIRouter(prefix="/api", tags=["chat"])


def _format_sse(event: ChatStreamEvent) -> dict:
    """Serialize a chat event to a Server-Sent Event dict."""
    return {
        "event": event.type,
        "data": event.model_dump_json(),
    }


@router.post("/chat/stream")
def chat_stream(request: ChatRequest) -> EventSourceResponse:
    """Stream a conversational answer as Server-Sent Events.

    Emits ``token`` events for each chunk, a ``sources`` event with citation
    documents, and finally a ``done`` event.  On failure an ``error`` event is
    emitted.
    """
    generator: Iterator[ChatStreamEvent] = answer_stream(
        message=request.message,
        history=request.history,
        session_id=request.session_id,
    )
    return EventSourceResponse(_format_sse(event) for event in generator)
