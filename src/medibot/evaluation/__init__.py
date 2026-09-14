"""Evaluation framework for MediBot.

Production-grade measurement of retrieval quality, answer accuracy, memory
continuity, citation quality, and safety.  See ``runner.py`` for the CLI
orchestrator and ``dashboard/`` for the visualization.
"""

from medibot.evaluation.evaluators import (
    AccuracyEvaluator,
    CitationEvaluator,
    MemoryEvaluator,
    RetrievalEvaluator,
    SafetyEvaluator,
)
from medibot.evaluation.judges import LLMJudge
from medibot.evaluation.metrics.retrieval_metrics import (
    hit_rate,
    mean_reciprocal_rank,
    mrr_at_k,
    recall_at_k,
)

__all__ = [
    "AccuracyEvaluator",
    "CitationEvaluator",
    "LLMJudge",
    "MemoryEvaluator",
    "RetrievalEvaluator",
    "SafetyEvaluator",
    "hit_rate",
    "mean_reciprocal_rank",
    "mrr_at_k",
    "recall_at_k",
]
