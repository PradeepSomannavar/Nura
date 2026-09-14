"""Intent classification / medical-domain guardrails service.

Every user message is classified before RAG.  The classifier first tries an
LLM (Gemini primary → Groq fallback) that returns a structured JSON intent;
if the LLM call fails or returns an invalid label, a deterministic keyword
heuristic is used.  Off-domain messages are rerouted to a polite refusal
without running retrieval.
"""

from __future__ import annotations

import logging
import re
from enum import StrEnum
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from medibot.core.config import settings
from medibot.prompts.intent import (
    CLASSIFY_INTENT_SYSTEM,
    REFUSAL_SYSTEM,
    STATIC_REFUSAL,
)
from medibot.services.llm import get_llm

logger = logging.getLogger(__name__)


class Intent(StrEnum):
    """Domain intent of a user message."""

    MEDICAL_QUERY = "MEDICAL_QUERY"
    NON_MEDICAL = "NON_MEDICAL"
    HARMFUL_REQUEST = "HARMFUL_REQUEST"


#: Markers that indicate an on-topic medical query (deterministic fallback).
_MEDICAL_MARKERS = (
    "symptom",
    "disease",
    "diagnosis",
    "diagnostic",
    "treatment",
    "medication",
    "medicine",
    "drug",
    "fever",
    "pain",
    "blood",
    "heart",
    "cancer",
    "tumor",
    "diabetes",
    "hypertension",
    "infection",
    "surgery",
    "syndrome",
    "disorder",
    "virus",
    "bacteria",
    "dose",
    "vaccine",
    "prescription",
    "anatomy",
    "bone",
    "muscle",
    "brain",
    "lung",
    "kidney",
    "liver",
    "skin",
    "rash",
    "headache",
    "nausea",
    "vomit",
    "fatigue",
    "joint",
    "injury",
    "wound",
    "dental",
    "pregnant",
    "pregnancy",
    "sleep",
    "anxiety",
    "depression",
    "blood pressure",
    "glucose",
    "cholesterol",
)

#: Regex to extract the ``intent`` value from an LLM JSON response.
_INTENT_RE = re.compile(r'"intent"\s*:\s*"([A-Z_]+)"', re.IGNORECASE)


def _keyword_classify(message: str) -> Intent:
    """Deterministic medical-intent heuristic used as a fallback."""
    lowered = message.lower()
    if any(mark in lowered for mark in _MEDICAL_MARKERS):
        return Intent.MEDICAL_QUERY
    return Intent.NON_MEDICAL


def _parse_intent(text: str) -> Intent | None:
    """Parse an intent label out of an LLM JSON response."""
    match = _INTENT_RE.search(text)
    if not match:
        return None
    label = match.group(1).upper()
    try:
        return Intent(label)
    except ValueError:
        return None


def _llm_classify(message: str, history: list[Any] | None = None) -> Intent | None:
    """Classify intent via the provider router (Gemini → Groq fallback).

    Returns ``None`` if the LLM call fails or returns an unrecognized label.
    """
    history_text = ""
    if history:
        lines = []
        for msg in history[-6:]:  # last ~3 turns
            role = getattr(msg, "role", "user")
            content = getattr(msg, "content", str(msg))
            lines.append(f"{role}: {content}")
        history_text = "\n".join(lines)

    prompt = f"Recent conversation:\n{history_text}\n\nLatest user message: {message}"
    try:
        llm = get_llm()
        result = llm.invoke([SystemMessage(content=CLASSIFY_INTENT_SYSTEM),
                             HumanMessage(content=prompt)])
        text = result.content if isinstance(result.content, str) else str(result.content)
        return _parse_intent(text)
    except Exception:  # noqa: BLE001 - any provider failure falls back to heuristic
        logger.warning("LLM intent classification failed; using heuristic", exc_info=True)
        return None


class IntentService:
    """Classify user messages and enforce medical-domain guardrails."""

    def classify(self, message: str, history: list[Any] | None = None) -> Intent:
        """Classify a message: LLM first, deterministic heuristic as fallback."""
        intent = _llm_classify(message, history) if settings.ENABLE_INTENT_GUARD else None
        if intent is not None:
            return intent
        return _keyword_classify(message)

    def is_medical(self, message: str, history: list[Any] | None = None) -> bool:
        """Return True if the message is an in-domain medical query."""
        return self.classify(message, history) is Intent.MEDICAL_QUERY

    def refusal_stream(self, message: str) -> list[str]:
        """Return refusal text chunks for an off-domain message.

        Tries the LLM (Gemini → Groq fallback) for a tailored, in-character
        refusal; on any failure returns a static professional refusal.
        """
        try:
            llm = get_llm()
            result = llm.invoke(
                [
                    SystemMessage(content=REFUSAL_SYSTEM),
                    HumanMessage(content=message),
                ]
            )
            text = result.content if isinstance(result.content, str) else str(result.content)
            text = text.strip()
            if text:
                return [text]
        except Exception:  # noqa: BLE001
            logger.warning("LLM refusal generation failed; using static text",
                           exc_info=True)
        return [STATIC_REFUSAL]


_intent_service: IntentService = IntentService()


def get_intent_service() -> IntentService:
    """Return the intent service singleton."""
    return _intent_service


def classify_intent(message: str, history: list[Any] | None = None) -> Intent:
    """Module-level convenience wrapper around the intent service."""
    return _intent_service.classify(message, history)
