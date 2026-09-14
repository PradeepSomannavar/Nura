"""Citation evaluator (bracket citations programmatic + judge accuracy)."""

from __future__ import annotations

import re
from typing import Any

from medibot.evaluation.evaluators.base import CaseOutcome, Evaluator
from medibot.evaluation.judges.llm_judge import LLMJudge

_CITATION_RE = re.compile(r"\[(\d+)\]")


class CitationEvaluator(Evaluator):
    """Verify the answer cites sources and the citations are grounded."""

    category = "citation"

    def __init__(self, chain: Any, judge: LLMJudge | None = None) -> None:
        self._chain = chain
        self._judge = judge or LLMJudge()

    def evaluate(self, case: dict[str, Any]) -> CaseOutcome:
        query = case["query"]
        min_citations = int(case.get("expected", {}).get("min_citations", 1))

        response = self._chain.invoke({"input": query, "chat_history": []})
        answer = str(response.get("answer", ""))
        context_docs = response.get("context", [])
        context = ", ".join(
            getattr(doc, "page_content", str(doc)) for doc in context_docs
        )

        found_citations = set(_CITATION_RE.findall(answer))
        programmatic_ok = len(found_citations) >= max(min_citations, 0)

        judgement = self._judge.score(
            category=self.category,
            question=query,
            answer=answer,
            context=context,
        )

        passed = programmatic_ok and judgement.passed()
        return CaseOutcome(
            case_id=case["id"],
            category=self.category,
            passed=passed,
            score=judgement.score,
            sub_scores=judgement.sub_scores,
            reasoning=judgement.reasoning,
            details={
                "query": query,
                "citations_found": sorted(found_citations),
                "programmatic_ok": programmatic_ok,
                "answer": answer[:500],
            },
        )
