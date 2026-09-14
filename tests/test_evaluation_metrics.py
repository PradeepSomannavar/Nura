"""Unit tests for programmatic retrieval metrics."""

from __future__ import annotations

import pytest

from medibot.evaluation.metrics.retrieval_metrics import (
    hit_rate,
    mean_reciprocal_rank,
    mrr_at_k,
    recall_at_k,
)


def test_recall_at_k_full_retrieval():
    """All relevant ids found within the top-k count as full recall."""
    assert recall_at_k(["a", "b"], ["a", "x", "b"], k=3) == 1.0


def test_recall_at_k_partial():
    """Retrieving one of two relevant ids yields 0.5 at k=1."""
    assert recall_at_k(["a", "b"], ["a", "b"], k=1) == 0.5


def test_recall_at_k_no_relevant():
    """Empty relevant set returns 0.0."""
    assert recall_at_k([], ["a", "b"]) == 0.0


def test_recall_at_k_none_matched():
    """No overlap yields 0.0."""
    assert recall_at_k(["a"], ["b", "c", "d"]) == 0.0


def test_hit_rate_present():
    """At least one relevant item retrieved yields 1.0."""
    assert hit_rate(["a"], ["x", "a"]) == 1.0


def test_hit_rate_absent():
    """No relevant item retrieved yields 0.0."""
    assert hit_rate(["a"], ["x", "y"]) == 0.0


def test_hit_rate_empty_relevant():
    """Empty relevant set yields 0.0."""
    assert hit_rate([], ["x"]) == 0.0


def test_mrr_at_k_first_result():
    """First-ranked relevant item yields 1.0."""
    assert mrr_at_k(["a"], ["a", "b", "c"]) == 1.0


def test_mrr_at_k_second_result():
    """Second-ranked relevant item yields 0.5."""
    assert mrr_at_k(["b"], ["x", "b", "c"]) == 0.5


def test_mrr_at_k_truncated():
    """Relevant item beyond k is excluded."""
    assert mrr_at_k(["b"], ["x", "b", "c"], k=1) == 0.0


def test_mean_reciprocal_rank_averages_pairs():
    """MRR averages reciprocal ranks across query pairs."""
    pairs = [
        (["a"], ["a", "b"]),  # rr = 1.0
        (["c"], ["x", "y", "c"]),  # rr = 1/3
    ]
    assert mean_reciprocal_rank(pairs) == pytest.approx(2 / 3)
