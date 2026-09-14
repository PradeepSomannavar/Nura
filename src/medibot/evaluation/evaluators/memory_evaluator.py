"""Memory continuity evaluator (multi-turn follow-up context use)."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from medibot.evaluation.evaluators.base import CaseOutcome, Evaluator
from medibot.evaluation.judges.llm_judge import LLMJudge


class MemoryEvaluator(Evaluator):
    """Feed a multi-turn conversation and judge context continuity."""

    category = "memory"

    def __init__(self, chain: Any, judge: LLMJudge | None = None) -> None:
        self._chain = chain
        self._judge = judge or LLMJudge()

    def evaluate(self, case: dict[str, Any]) -> CaseOutcome:
        conversation = list(case["conversation"])
        final_question = conversation[-1]
        expected = case.get("expected", {}).get("points", [])

        history: list[Any] = []
        for turn in conversation[:-1]:
            response = self._chain.invoke({"input": turn, "chat_history": history})
            history.append(HumanMessage(content=turn))
            history.append(AIMessage(content=str(response.get("answer", ""))))

        final_response = self._chain.invoke(
            {"input": final_question, "chat_history": history}
        )
        answer = str(final_response.get("answer", ""))
        prior_context = "\n".join(
            f"{m.type}: {m.content}" for m in history
        )

        judgement = self._judge.score(
            category=self.category,
            question=final_question,
            answer=answer,
            expected=expected,
            context=prior_context,
        )

        return CaseOutcome(
            case_id=case["id"],
            category=self.category,
            passed=judgement.passed(),
            score=judgement.score,
            sub_scores=judgement.sub_scores,
            reasoning=judgement.reasoning,
            details={
                "turns": len(conversation),
                "final_question": final_question,
                "answer": answer[:500],
            },
        )
