"""Smoke tests for evaluators and the evaluation runner (stubbed LLM/deps)."""

from __future__ import annotations

from langchain_core.documents import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from medibot.core.database import Base
from medibot.evaluation import runner
from medibot.evaluation.evaluators import (
    AccuracyEvaluator,
    CitationEvaluator,
    MemoryEvaluator,
    RetrievalEvaluator,
    SafetyEvaluator,
)
from medibot.evaluation.judges.llm_judge import JudgeResult
from medibot.services.intent import Intent


class _FakeSearch:
    """Fake vectorstore similarity search returning keyword-matching docs."""

    def similarity_search(self, query: str, k: int = 5):
        return [
            Document(page_content="blood pressure hypertension systolic diastolic"),
            Document(page_content="diabetes blood glucose HbA1c fasting"),
            Document(page_content="unrelated text about cooking"),
        ][:k]


class _FakeJudge:
    """Stub LLM judge returning a fixed pass."""

    def score(self, **kwargs):
        return JudgeResult(
            category=kwargs["category"],
            score=9.0,
            sub_scores={"relevance": 9.0},
            reasoning="stub judge",
        )


class _FakeChain:
    """Stub RAG chain that echoes a canned answer and threads history."""

    def __init__(self) -> None:
        self.history: list = []

    def invoke(self, payload: dict) -> dict:
        self.history = payload.get("chat_history", self.history)
        answer = (
            "Based on the context, hypertension commonly has no symptoms "
            "and is called the silent killer. [1] "
            "For reference only, not a substitute for professional medical advice."
        )
        return {
            "answer": answer,
            "context": [
                Document(page_content="blood pressure hypertension silent killer"),
            ],
        }


class _FakeIntent:
    """Stub intent service: refuses a specific query, allows the rest."""

    def classify(self, message: str, history: list | None = None) -> Intent:
        return Intent.NON_MEDICAL if "sourdough" in message else Intent.MEDICAL_QUERY

    def refusal_stream(self, message: str) -> list[str]:
        return ["I can only help with medical questions."]


def test_retrieval_evaluator_hit_rate():
    """Retrieval evaluator scores keyword recall in the top-k."""
    eval_ = RetrievalEvaluator(search_fn=_FakeSearch().similarity_search)
    case = {
        "id": "r1",
        "query": "hypertension",
        "expected": {"keywords": ["blood pressure", "hypertension"]},
        "min_hit_rate": 0.5,
    }
    outcome = eval_.evaluate(case)
    assert outcome.passed is True
    assert outcome.score == 10.0
    assert outcome.sub_scores["keyword_hit_rate"] == 1.0


def test_retrieval_evaluator_fails_on_missing_keywords():
    """Retrieval evaluator fails when expected keywords are absent."""
    eval_ = RetrievalEvaluator(search_fn=_FakeSearch().similarity_search)
    case = {
        "id": "r2",
        "query": "unknown topic",
        "expected": {"keywords": ["zygote", "quantum"]},
        "min_hit_rate": 0.5,
    }
    outcome = eval_.evaluate(case)
    assert outcome.passed is False
    assert outcome.score == 0.0


def test_accuracy_evaluator_uses_judge():
    """Accuracy evaluator invokes the RAG chain and judge."""
    eval_ = AccuracyEvaluator(chain=_FakeChain(), judge=_FakeJudge())
    case = {
        "id": "a1",
        "query": "What are hypertension symptoms?",
        "expected": {"points": ["no symptoms", "silent killer"]},
    }
    outcome = eval_.evaluate(case)
    assert outcome.passed is True
    assert outcome.score == 9.0
    assert outcome.details["answer"]


def test_memory_evaluator_threads_history():
    """Memory evaluator threads prior turns as chat_history."""
    eval_ = MemoryEvaluator(chain=_FakeChain(), judge=_FakeJudge())
    case = {
        "id": "m1",
        "conversation": ["I have hypertension.", "What should I expect?"],
        "expected": {"points": ["references hypertension"]},
    }
    outcome = eval_.evaluate(case)
    assert outcome.passed is True
    assert len(eval_._chain.history) >= 2


def test_citation_evaluator_requires_bracket_citations():
    """Citation evaluator fails when the answer has no [n] citations."""
    passing = CitationEvaluator(chain=_FakeChain(), judge=_FakeJudge())
    outcome = passing.evaluate(
        {"id": "c1", "query": "risk factors", "expected": {"min_citations": 1}}
    )
    assert outcome.passed is True
    assert outcome.details["programmatic_ok"] is True

    class _NoCitations(_FakeChain):
        def invoke(self, payload: dict) -> dict:
            return {
                "answer": "Plain answer with no citations.",
                "context": [Document(page_content="context")],
            }

    failing = CitationEvaluator(chain=_NoCitations(), judge=_FakeJudge())
    outcome = failing.evaluate(
        {"id": "c2", "query": "risk factors", "expected": {"min_citations": 1}}
    )
    assert outcome.passed is False


def test_safety_evaluator_refusal():
    """Off-domain requests must be refused, not answered."""
    eval_ = SafetyEvaluator(chain=_FakeChain(), intent_service=_FakeIntent(), judge=_FakeJudge())
    outcome = eval_.evaluate(
        {"id": "s1", "type": "refusal", "query": "How do I bake a sourdough loaf?"}
    )
    assert outcome.passed is True
    assert outcome.details["intent"] == "NON_MEDICAL"


def test_safety_evaluator_no_disclaimer_required():
    """Medical answers no longer require a mandatory disclaimer."""

    class _NoDisclaimerChain(_FakeChain):
        def invoke(self, payload: dict) -> dict:
            return {
                "answer": (
                    "Hypertension commonly has no symptoms and is called the silent killer. [1]"
                ),
                "context": [
                    Document(page_content="blood pressure hypertension silent killer"),
                ],
            }

    eval_ = SafetyEvaluator(
        chain=_NoDisclaimerChain(), intent_service=_FakeIntent(), judge=_FakeJudge()
    )
    outcome = eval_.evaluate(
        {
            "id": "s2",
            "type": "disclaimer",
            "query": "migraine treatment",
            "min_matches": 0,
            "expected": {"disclaimer_keywords": []},
        }
    )
    assert outcome.passed is True
    assert outcome.details["programmatic_ok"] is True


def _in_memory_db(monkeypatch):
    """Point runner DB persistence at a fresh in-memory SQLite."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    monkeypatch.setattr(runner, "SessionLocal", testing_session)
    monkeypatch.setattr(runner, "init_db", lambda: None)


def test_runner_retrieval_persists_and_reports(monkeypatch, tmp_path):
    """Runner evaluates retrieval cases and writes a report + DB run."""
    _in_memory_db(monkeypatch)

    report = runner.run(
        categories=["retrieval"],
        limit=1,
        save_db=True,
        report_dir=tmp_path,
        sleep_seconds=0.0,
        vectorstore=_FakeSearch(),
    )

    assert report["status"] == "completed"
    assert report["overall_score"] >= 0
    assert report["case_count"] == 1
    assert "retrieval" in report["category_scores"]

    written = list(tmp_path.glob("evaluation-*.json"))
    assert len(written) == 1

    db = runner.SessionLocal()
    try:
        run_row = db.query(runner.EvaluationRun).one()
        assert run_row.case_count == 1
        assert run_row.category_scores["retrieval"]["total"] == 1
        result_row = db.query(runner.EvaluationCaseResult).one()
        assert result_row.category == "retrieval"
    finally:
        db.close()
