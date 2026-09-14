"""Base classes for evaluation evaluators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CaseOutcome:
    """Result of evaluating a single case."""

    case_id: str
    category: str
    passed: bool
    score: float
    sub_scores: dict[str, float] = field(default_factory=dict)
    reasoning: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class Evaluator(ABC):
    """Base class for a single evaluation category."""

    category: str = ""

    @abstractmethod
    def evaluate(self, case: dict[str, Any]) -> CaseOutcome:
        """Evaluate one dataset case and return its outcome."""
