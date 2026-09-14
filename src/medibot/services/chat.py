"""Chat orchestration service.

Wraps the RAG chain into a streaming generator of events so the api/ router
stays thin.  Assembles memory context, streams answer tokens, and records
analytics metrics.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from medibot.schemas.chat import ChatMessageIn, ChatStreamEvent, SourceDoc
from medibot.services.analytics import RequestMetric, get_analytics_service
from medibot.services.intent import Intent, IntentService, get_intent_service
from medibot.services.llm import clean_stream_prefixes, get_active_provider
from medibot.services.memory import HybridMemory
from medibot.services.rag import build_rag_chain
from medibot.services.retrieval import load_vectorstore

logger = logging.getLogger(__name__)

_rag_chain: Any | None = None


def _get_rag_chain() -> Any:
    """Build the RAG chain once per process."""
    global _rag_chain
    if _rag_chain is None:
        vectorstore = load_vectorstore()
        _rag_chain = build_rag_chain(vectorstore)
    return _rag_chain


def _to_langchain_messages(history: list[ChatMessageIn]) -> list[BaseMessage]:
    """Convert DTO history into LangChain messages."""
    messages: list[BaseMessage] = []
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        else:
            messages.append(AIMessage(content=msg.content))
    return messages


def answer_stream(
    message: str,
    history: list[ChatMessageIn],
    session_id: int | None = None,
    memory: HybridMemory | None = None,
    intent_service: IntentService | None = None,
) -> Iterator[ChatStreamEvent]:
    """Stream a chat answer, yielding token/source/done events.

    Classifies intent first; off-domain (non-medical / harmful) messages are
    rerouted to a polite refusal without running retrieval or the RAG chain.
    """
    memory = memory or HybridMemory(session_id=session_id)
    intent_service = intent_service or get_intent_service()
    metrics = RequestMetric(session_id=session_id)
    provider = get_active_provider()
    metrics.provider = provider
    metrics.model = provider

    chat_history = _to_langchain_messages(history)
    context = memory.build_context(chat_history)

    if session_id is not None:
        memory.add_message("user", message)

    intent = intent_service.classify(message, history)

    yield ChatStreamEvent(type="meta", content=intent.value, provider=provider)
    logger.info("chat session=%s intent=%s provider=%s", session_id, intent, provider)

    if intent is not Intent.MEDICAL_QUERY:
        # Off-domain / harmful: stream a refusal, no retrieval, no RAG.
        start = time.perf_counter()
        refusal_parts: list[str] = []
        for chunk in intent_service.refusal_stream(message):
            refusal_parts.append(chunk)
            yield ChatStreamEvent(type="token", content=chunk, provider=provider)
        metrics.total_ms = round((time.perf_counter() - start) * 1000, 1)
        get_analytics_service().record(metrics)
        if session_id is not None:
            memory.add_message("assistant", "".join(refusal_parts))
        yield ChatStreamEvent(type="done", provider=provider)
        return

    rag_chain = _get_rag_chain()
    start = time.perf_counter()

    full = ""
    sources: list[SourceDoc] = []
    context_docs: list[Any] = []

    try:
        history_msgs = context.history_messages()
        stream = rag_chain.stream(
            {"input": message, "chat_history": history_msgs}
        )
        answer_deltas = []
        for chunk in stream:
            if "answer" in chunk and chunk["answer"]:
                answer_deltas.append(chunk["answer"])
            if "context" in chunk and chunk["context"]:
                context_docs = chunk["context"]
        for delta in clean_stream_prefixes(iter(answer_deltas)):
            full += delta
            yield ChatStreamEvent(type="token", content=delta, provider=provider)
        if context_docs:
            sources = [
                SourceDoc(content=d.page_content, metadata=dict(d.metadata or {}))
                for d in context_docs
            ]
        yield ChatStreamEvent(type="sources", sources=sources, provider=provider)

        metrics.total_ms = round((time.perf_counter() - start) * 1000, 1)
        get_analytics_service().record(metrics)

        if session_id is not None:
            memory.add_message("assistant", full)
            memory.evict_and_summarize()

        yield ChatStreamEvent(type="done", provider=provider)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat streaming failed")
        metrics.total_ms = round((time.perf_counter() - start) * 1000, 1)
        get_analytics_service().record(metrics)
        yield ChatStreamEvent(type="error", content=str(exc))
