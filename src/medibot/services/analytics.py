"""Analytics service stub.

Phase 1 scaffold for request/response metrics accumulation.  A durable
analytics store (SQLite + dashboard) is added in Phase 5.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

logger = logging.getLogger(__name__)


@dataclass
class RequestMetric:
    """Latency / provider metrics for a single LLM+RAG request."""

    session_id: int | None = None
    cache_hit: bool = False
    retrieval_ms: float | None = None
    llm_ms: float | None = None
    total_ms: float | None = None
    provider: str | None = None
    model: str | None = None


class AnalyticsService:
    """Accumulates request metrics in memory (stubbed for now)."""

    def __init__(self) -> None:
        self._metrics: list[RequestMetric] = []

    def record(self, metric: RequestMetric) -> None:
        self._metrics.append(metric)
        logger.info(
            "metrics provider=%s cache_hit=%s total_ms=%s",
            metric.provider,
            metric.cache_hit,
            metric.total_ms,
        )

    def snapshot(self) -> list[dict]:
        """Return a list of recorded metrics (for debugging/health)."""
        return [asdict(m) for m in self._metrics]


_analytics: AnalyticsService = AnalyticsService()


def get_analytics_service() -> AnalyticsService:
    """Return the analytics service singleton."""
    return _analytics
