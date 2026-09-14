"""Tests for the intent classifier and domain guardrails."""

from __future__ import annotations

from typing import Any

import pytest

from medibot.services import chat as chat_service
from medibot.services.intent import (
    Intent,
    _keyword_classify,
    _parse_intent,
)


@pytest.mark.parametrize(
    "message,expected",
    [
        ("What are the symptoms of hypertension?", Intent.MEDICAL_QUERY),
        ("How is diabetes diagnosed?", Intent.MEDICAL_QUERY),
        ("What medications treat anxiety?", Intent.MEDICAL_QUERY),
        ("My child has a fever and rash", Intent.MEDICAL_QUERY),
        ("How do I bake a chocolate cake?", Intent.NON_MEDICAL),
        ("What's the weather today?", Intent.NON_MEDICAL),
        ("Tell me a joke", Intent.NON_MEDICAL),
        ("Can you fix my python code?", Intent.NON_MEDICAL),
    ],
)
def test_keyword_classify(message, expected):
    """The deterministic heuristic correctly routes medical vs non-medical."""
    assert _keyword_classify(message) is expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ('{"intent": "MEDICAL_QUERY", "reason": "x"}', Intent.MEDICAL_QUERY),
        ('{"intent": "NON_MEDICAL"}', Intent.NON_MEDICAL),
        ('{"intent": "HARMFUL_REQUEST"}', Intent.HARMFUL_REQUEST),
        ("I think it is a medical question", None),
        ("garbage response", None),
    ],
)
def test_parse_intent(text, expected):
    """JSON intent label is parsed robustly; invalid text yields None."""
    assert _parse_intent(text) is expected


class _StubIntentService:
    """Stub that always classifies as NON_MEDICAL with a fixed refusal."""

    def classify(self, message: str, history: list[Any] | None = None) -> Intent:
        return Intent.NON_MEDICAL

    def refusal_stream(self, message: str) -> list[str]:
        return ["I can only help with medical questions."]


def test_non_medical_does_not_run_rag(monkeypatch):
    """Off-domain messages skip retrieval and RAG entirely."""
    called_rag = []
    monkeypatch.setattr(chat_service, "_get_rag_chain", lambda: called_rag.append(1))
    monkeypatch.setattr(
        chat_service,
        "load_vectorstore",
        lambda: called_rag.append("vectorstore"),
    )

    events = list(
        chat_service.answer_stream(
            "What's the weather?",
            history=[],
            intent_service=_StubIntentService(),
        )
    )

    types = [e.type for e in events]
    assert types == ["meta", "token", "done"]
    assert events[0].content == Intent.NON_MEDICAL.value
    assert "medical" in events[1].content
    # No RAG chain / vectorstore loaded for a non-medical message.
    assert called_rag == []
