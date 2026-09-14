"""Programmatic retrieval metrics (no LLM required)."""

from __future__ import annotations

from collections.abc import Sequence


def recall_at_k(
    relevant_ids: Sequence[str] | Sequence[int],
    retrieved_ids: Sequence[str] | Sequence[int],
    k: int | None = None,
) -> float:
    """Fraction of relevant items retrieved within the top ``k`` results.

    ``k`` defaults to the length of ``retrieved_ids``.  Returns 0.0 when there
    are no relevant items.
    """
    relevant = set(relevant_ids)
    if not relevant:
        return 0.0
    top = retrieved_ids[:k] if k is not None else retrieved_ids
    hits = sum(1 for doc_id in top if doc_id in relevant)
    return hits / len(relevant)


def hit_rate(
    relevant_ids: Sequence[str] | Sequence[int],
    retrieved_ids: Sequence[str] | Sequence[int],
) -> float:
    """1.0 if at least one relevant item appears in the retrieved list."""
    relevant = set(relevant_ids)
    if not relevant:
        return 0.0
    return 1.0 if any(doc_id in relevant for doc_id in retrieved_ids) else 0.0


def _reciprocal_rank(
    relevant_ids: Sequence[str] | Sequence[int],
    retrieved_ids: Sequence[str] | Sequence[int],
) -> float:
    """Reciprocal rank: 1/rank of the first relevant result (0.0 if none)."""
    relevant = set(relevant_ids)
    for rank, doc_id in enumerate(retrieved_ids, start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def mrr_at_k(
    relevant_ids: Sequence[str] | Sequence[int],
    retrieved_ids: Sequence[str] | Sequence[int],
    k: int | None = None,
) -> float:
    """Reciprocal rank of the first relevant result inside the top ``k``."""
    top = retrieved_ids[:k] if k is not None else retrieved_ids
    return _reciprocal_rank(relevant_ids, top)


def mean_reciprocal_rank(
    queries: Sequence[tuple[Sequence[str] | Sequence[int], Sequence[str] | Sequence[int]]],
    k: int | None = None,
) -> float:
    """Mean reciprocal rank across query (relevant, retrieved) pairs."""
    if not queries:
        return 0.0
    total = sum(mrr_at_k(rel, ret, k=k) for rel, ret in queries)
    return total / len(queries)
