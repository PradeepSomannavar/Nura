"""Accuracy evaluator (RAG answer judged against expected points)."""

from __future__ import annotations

from typing import Any

from medibot.evaluation.evaluators.base import CaseOutcome, Evaluator
from medibot.evaluation.judges.llm_judge import LLMJudge


class AccuracyEvaluator(Evaluator):
    """Run the RAG chain and judge answer relevance/correctness/completeness."""

    category = "accuracy"

    def __init__(self, chain: Any, judge: LLMJudge | None = None) -> None:
        self._chain = chain
        self._judge = judge or LLMJudge()

    def evaluate(self, case: dict[str, Any]) -> CaseOutcome:
        query = case["query"]
        expected = case.get("expected", {})
        points = expected.get("points", [])

        response = self._chain.invoke({"input": query, "chat_history": []})
        answer = str(response.get("answer", ""))
        context = ", ".join(
            getattr(doc, "page_content", str(doc))
            for doc in response.get("context", [])
        )

        judgement = self._judge.score(
            category=self.category,
            question=query,
            answer=answer,
            expected=points,
            context=context,
        )

        return CaseOutcome(
            case_id=case["id"],
            category=self.category,
            passed=judgement.passed(),
            score=judgement.score,
            sub_scores=judgement.sub_scores,
            reasoning=judgement.reasoning,
            details={
                "query": query,
                "answer": answer[:500],
                "expected_points": points,
            },
        )
