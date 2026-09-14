"""LLM-as-a-Judge for qualitative evaluation categories."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from medibot.prompts.judge import build_judge_system
from medibot.services.llm import get_llm

logger = logging.getLogger(__name__)


@dataclass
class JudgeResult:
    """Structured judgement for a single case."""

    category: str
    score: float
    sub_scores: dict[str, float] = field(default_factory=dict)
    reasoning: str = ""

    def passed(self, threshold: float = 7.0) -> bool:
        """A case passes when its overall score meets the threshold."""
        return self.score >= threshold


class LLMJudge:
    """Scores assistant responses against a category rubric via the LLM.

    Uses the Phase-2 provider router (Gemini primary → Groq fallback).  On any
    provider failure the judge returns a neutral score (0.0) plus reasoning so
    the run never crashes.
    """

    def __init__(self, llm: Any | None = None) -> None:
        self._llm = llm if llm is not None else get_llm()

    def score(
        self,
        *,
        category: str,
        question: str,
        answer: str,
        expected: object = None,
        context: str | None = None,
    ) -> JudgeResult:
        """Score an answer against the rubric for ``category``."""
        system = SystemMessage(content=build_judge_system(category))
        user = HumanMessage(
            content=(
                f"QUESTION:\n{question}\n\n"
                f"EXPECTED (if any):\n{expected if expected is not None else '(none)'}\n\n"
                f"RETRIEVED CONTEXT (if any):\n{context or '(none)'}\n\n"
                f"ASSISTANT ANSWER:\n{answer}\n\n"
                "Return the JSON score object."
            )
        )
        try:
            response = self._llm.invoke([system, user])
            text = response.content if isinstance(response, object) else ""
            if isinstance(text, list):
                parts = [str(p.get("text", "")) for p in text if isinstance(p, dict)]
                text = " ".join(parts)
            elif not isinstance(text, str):
                text = str(text or "")
            return _parse_judgement(category, text)
        except Exception as exc:  # noqa: BLE001 - judge must degrade gracefully
            logger.warning("LLM judge failed for %s: %s", category, exc)
            return JudgeResult(
                category=category,
                score=0.0,
                reasoning=f"Judge failure: {exc}",
            )


def _parse_judgement(category: str, text: str) -> JudgeResult:
    """Parse the judge's JSON payload into a JudgeResult (robust)."""
    data: dict[str, Any] = {}
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        logger.warning("Could not parse judge JSON; treating output as reasoning only")

    if not data:
        return JudgeResult(category=category, score=0.0, reasoning=text[:500])

    try:
        score = float(data.get("score", 0.0))
    except (TypeError, ValueError):
        score = 0.0

    sub_scores = _coerce_scores(data.get("sub_scores"))
    reasoning = str(data.get("reasoning", ""))
    return JudgeResult(
        category=category,
        score=max(0.0, min(10.0, score)),
        sub_scores=sub_scores,
        reasoning=reasoning,
    )


def _coerce_scores(raw: object) -> dict[str, float]:
    """Convert a raw sub-scores mapping into floats (bounded 0-10)."""
    out: dict[str, float] = {}
    if not isinstance(raw, dict):
        return out
    for key, value in raw.items():
        try:
            out[str(key)] = max(0.0, min(10.0, float(value)))
        except (TypeError, ValueError):
            continue
    return out
