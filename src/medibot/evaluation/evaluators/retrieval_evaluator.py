"""Retrieval evaluator (programmatic keyword recall, no LLM)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from medibot.evaluation.evaluators.base import CaseOutcome, Evaluator
from medibot.services.retrieval import similarity_search


class RetrievalEvaluator(Evaluator):
    """Measure retrieval quality via expected-keyword recall in the top-k."""

    category = "retrieval"

    def __init__(
        self,
        search_fn: Callable[[str, int], list[Any]] | None = None,
        default_k: int = 5,
    ) -> None:
        self._search = search_fn or similarity_search
        self._default_k = default_k

    def evaluate(self, case: dict[str, Any]) -> CaseOutcome:
        query = case["query"]
        k = int(case.get("k", self._default_k))
        min_hit_rate = float(case.get("min_hit_rate", 0.5))

        documents = self._search(query, k)
        retrieved_text = " ".join(
            doc.page_content.lower() if hasattr(doc, "page_content") else str(doc).lower()
            for doc in documents
        )

        keywords = [str(kw) for kw in case["expected"]["keywords"]]
        hits = sum(1 for kw in keywords if kw.lower() in retrieved_text)
        hit_rate = hits / len(keywords) if keywords else 0.0

        passed = hit_rate >= min_hit_rate
        return CaseOutcome(
            case_id=case["id"],
            category=self.category,
            passed=passed,
            score=round(hit_rate * 10, 2),
            sub_scores={"keyword_hit_rate": round(hit_rate, 3)},
            reasoning=(
                f"{hits}/{len(keywords)} expected keywords found in top-{k}"
                if keywords
                else "No expected keywords defined"
            ),
            details={
                "query": query,
                "k": k,
                "docs_returned": len(documents),
                "keywords": keywords,
            },
        )
