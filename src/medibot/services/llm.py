"""Multi-provider LLM service (Gemini primary → Groq fallback).

Gemini is the primary provider; on failure (rate limit / server error) the
request transparently falls back to Groq.  The active provider is reported
for analytics/cost tracking but never contains secrets.
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from enum import StrEnum
from typing import Any

from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGenerationChunk, ChatResult
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai._enums import HarmBlockThreshold, HarmCategory
from langchain_groq import ChatGroq

from medibot.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(StrEnum):
    """Identifiers for the supported LLM providers."""

    GEMINI = "gemini"
    GROQ = "groq"


_PROVIDER_ORDER = (LLMProvider.GEMINI, LLMProvider.GROQ)


def _gemini_safety_settings() -> dict:
    """Safety thresholds for the medical assistant.

    A medical tool keeps sensible blocking on harmful categories (unlike a
    movie-recommendation app which may opt to block nothing).
    """
    return {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }


def _build_chat_model(provider: LLMProvider) -> BaseChatModel:
    """Construct a configured LangChain chat model for a provider."""
    temperature = settings.LLM_TEMPERATURE
    max_tokens = settings.LLM_MAX_TOKENS
    streaming = settings.ENABLE_STREAMING

    if provider == LLMProvider.GEMINI:
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set")
        logger.info("Initializing Gemini LLM: %s", settings.GEMINI_MODEL)
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            safety_settings=_gemini_safety_settings(),
        )

    if provider == LLMProvider.GROQ:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set")
        logger.info("Initializing Groq LLM: %s", settings.GROQ_MODEL)
        return ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
        )

    raise ValueError(f"Unknown provider: {provider}")


class FallbackChatModel(BaseChatModel):
    """A LangChain chat model that falls back to the next provider on failure.

    ``primary`` is tried first; if it raises, the request is retried on each
    fallback in order.  The ``provider`` attribute reflects the model that last
    served a request.
    """

    models: dict[LLMProvider, BaseChatModel]
    order: tuple[LLMProvider, ...]
    provider: LLMProvider = LLMProvider.GROQ

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        last_error: Exception | None = None
        for name in self.order:
            model = self.models[name]
            try:
                result = model._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                self.provider = name
                return result
            except Exception as exc:  # noqa: BLE001  - fallback on any provider error
                last_error = exc
                logger.warning("Provider %s failed (%s); trying next", name, exc)
        raise RuntimeError("All LLM providers failed") from last_error

    def _stream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        last_error: Exception | None = None
        for name in self.order:
            model = self.models[name]
            try:
                iterator = model._stream(messages, stop=stop, run_manager=run_manager, **kwargs)

                def _first(iterable: Iterator[ChatGenerationChunk]) -> ChatGenerationChunk | None:
                    try:
                        return next(iterable)
                    except StopIteration:
                        return None

                first = _first(iterator)
                if first is None:
                    return
                self.provider = name
                yield first
                yield from iterator
                return
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                logger.warning("Provider %s stream failed (%s); trying next", name, exc)
        raise RuntimeError("All LLM providers failed") from last_error

    @property
    def _llm_type(self) -> str:
        return "fallback-chat-model"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"order": [p.value for p in self.order]}


_configured: list[LLMProvider] | None = None


def _configured_providers() -> list[LLMProvider]:
    """Providers with an API key set, in priority order."""
    global _configured
    if _configured is not None:
        return _configured
    configured: list[LLMProvider] = []
    for name in _PROVIDER_ORDER:
        key = settings.GEMINI_API_KEY if name is LLMProvider.GEMINI else settings.GROQ_API_KEY
        if key:
            configured.append(name)
    _configured = configured
    return configured


_active_model: FallbackChatModel | None = None


def get_llm() -> FallbackChatModel:
    """Return a fallback chat model over all configured providers.

    The instance is cached per process.  Raises ``ValueError`` if no provider
    API key is configured.
    """
    global _active_model
    if _active_model is not None:
        return _active_model

    providers = _configured_providers()
    if not providers:
        raise ValueError(
            "No LLM provider configured. Set GEMINI_API_KEY and/or GROQ_API_KEY in .env"
        )

    models = {name: _build_chat_model(name) for name in providers}
    _active_model = FallbackChatModel(
        models=models,
        order=tuple(providers),
        provider=providers[0],
    )
    return _active_model


def get_active_provider() -> str | None:
    """Return the provider that last served a request (for analytics)."""
    if _active_model is not None:
        return _active_model.provider.value
    return None


#: Common prefixes some models prepend to their first streamed token.
_STREAM_PREFIXES = (
    "assistant:",
    "medi bot:",
    "medibot:",
    "bot:",
    "ai:",
    "cinephilegpt:",
    "user:",
)


def clean_stream_prefixes(chunks: Iterator[str]) -> Iterator[str]:
    """Strip common model prefixes from the leading streamed chunks.

    Some models prepend ``assistant:`` / ``MediBot:`` style labels to the
    first token.  This generator drops such prefixes so the UI never renders
    them.  Prefix matching is case-insensitive and only applied to the first
    non-empty chunk.
    """
    emitted = False
    for chunk in chunks:
        if not emitted:
            chunk = chunk.lstrip()
            lowered = chunk.lower()
            for prefix in _STREAM_PREFIXES:
                if lowered.startswith(prefix):
                    chunk = chunk[len(prefix):].lstrip()
                    break
            emitted = True
        yield chunk
