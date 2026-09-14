"""Tests for the multi-provider LLM router and stream prefix cleaning."""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from medibot.services.llm import (
    FallbackChatModel,
    LLMProvider,
    _configured_providers,
    clean_stream_prefixes,
)


class FakeChatModel(BaseChatModel):
    """A real BaseChatModel subclass that can be configured to fail."""

    name: str = "fake"
    fail: bool = False
    text: str = "ok"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        if self.fail:
            raise RuntimeError("provider failure")
        return ChatResult(generations=[ChatGeneration(message=HumanMessage(content=self.text))])

    @property
    def _llm_type(self) -> str:
        return "fake-chat-model"


def _fake_model(name: str, error: bool = False, text: str = "ok") -> FakeChatModel:
    return FakeChatModel(name=name, fail=error, text=text)


def test_configured_providers_priority(monkeypatch):
    """Gemini comes before Groq when both keys are set."""
    monkeypatch.setattr("medibot.services.llm.settings.GEMINI_API_KEY", "k1")
    monkeypatch.setattr("medibot.services.llm.settings.GROQ_API_KEY", "k2")
    monkeypatch.setattr("medibot.services.llm._configured", None)
    order = _configured_providers()
    assert order == [LLMProvider.GEMINI, LLMProvider.GROQ]


def test_configured_providers_only_groq(monkeypatch):
    """Groq is used when Gemini key is absent."""
    monkeypatch.setattr("medibot.services.llm.settings.GEMINI_API_KEY", "")
    monkeypatch.setattr("medibot.services.llm.settings.GROQ_API_KEY", "k2")
    monkeypatch.setattr("medibot.services.llm._configured", None)
    assert _configured_providers() == [LLMProvider.GROQ]


def test_configured_providers_none(monkeypatch):
    """No configured providers raises in get_llm."""
    monkeypatch.setattr("medibot.services.llm.settings.GEMINI_API_KEY", "")
    monkeypatch.setattr("medibot.services.llm.settings.GROQ_API_KEY", "")
    monkeypatch.setattr("medibot.services.llm._configured", None)
    from medibot.services.llm import get_llm

    with pytest.raises(ValueError):
        get_llm()


def test_fallback_on_primary_failure():
    """FallbackChatModel retries on the backup when primary raises."""
    primary = _fake_model("gemini", error=True)
    backup = _fake_model("groq", text="fallback answer")
    model = FallbackChatModel(
        models={
            LLMProvider.GEMINI: primary,
            LLMProvider.GROQ: backup,
        },
        order=(LLMProvider.GEMINI, LLMProvider.GROQ),
        provider=LLMProvider.GEMINI,
    )
    result = model.invoke([HumanMessage(content="hi")])
    assert result.content == "fallback answer"
    assert model.provider == LLMProvider.GROQ


def test_no_fallback_when_primary_succeeds():
    """FallbackChatModel uses the primary when it succeeds."""
    primary = _fake_model("gemini", text="primary answer")
    backup = _fake_model("groq")
    model = FallbackChatModel(
        models={LLMProvider.GEMINI: primary, LLMProvider.GROQ: backup},
        order=(LLMProvider.GEMINI, LLMProvider.GROQ),
        provider=LLMProvider.GEMINI,
    )
    result = model.invoke([HumanMessage(content="hi")])
    assert result.content == "primary answer"
    assert model.provider == LLMProvider.GEMINI


def test_clean_stream_prefixes_assistant():
    """'assistant:' prefix is stripped from the leading chunk."""
    out = list(clean_stream_prefixes(iter(["assistant: ", "Hello", " world"])))
    assert "".join(out) == "Hello world"


def test_clean_stream_prefixes_medibot():
    """'MediBot:' prefix is stripped (case-insensitive)."""
    out = list(clean_stream_prefixes(iter(["MediBot:", "Hi"])))
    assert "".join(out) == "Hi"


def test_clean_stream_prefixes_no_prefix():
    """Plain text with no prefix is unchanged."""
    assert "".join(clean_stream_prefixes(iter(["Hello world"]))) == "Hello world"
