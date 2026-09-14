"""Evaluation runner: CLI orchestrator for the evaluation framework."""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Any

from medibot.core.config import PROJECT_ROOT
from medibot.core.database import SessionLocal, init_db
from medibot.evaluation.evaluators import (
    AccuracyEvaluator,
    CaseOutcome,
    CitationEvaluator,
    Evaluator,
    MemoryEvaluator,
    RetrievalEvaluator,
    SafetyEvaluator,
)
from medibot.evaluation.judges.llm_judge import LLMJudge
from medibot.models.evaluation import EvaluationCaseResult, EvaluationRun
from medibot.services.rag import build_rag_chain

logger = logging.getLogger(__name__)

#: Map evaluation categories to their dataset files.
DATASET_FILES: dict[str, str] = {
    "retrieval": "retrieval_eval.json",
    "accuracy": "accuracy_eval.json",
    "memory": "memory_eval.json",
    "citation": "citation_eval.json",
    "safety": "safety_eval.json",
}

DEFAULT_REPORT_DIR = PROJECT_ROOT / "reports"

DATASETS_DIR = Path(__file__).resolve().parent / "datasets"


def load_cases(category: str) -> list[dict[str, Any]]:
    """Load the JSON test cases for a category."""
    filename = DATASET_FILES[category]
    with (DATASETS_DIR / filename).open(encoding="utf-8") as handle:
        return json.load(handle)


def build_evaluator(
    category: str,
    chain: Any | None = None,
    vectorstore: Any | None = None,
    judge: LLMJudge | None = None,
) -> Evaluator:
    """Construct the evaluator for a category with shared dependencies."""
    if category == "retrieval":
        vs = vectorstore
        if vs is None:
            from medibot.services.retrieval import load_vectorstore

            vs = load_vectorstore()
        return RetrievalEvaluator(search_fn=vs.similarity_search)

    if chain is None:
        raise ValueError("chain is required for non-retrieval categories")

    if category == "accuracy":
        return AccuracyEvaluator(chain=chain, judge=judge)
    if category == "memory":
        return MemoryEvaluator(chain=chain, judge=judge)
    if category == "citation":
        return CitationEvaluator(chain=chain, judge=judge)
    if category == "safety":
        from medibot.services.intent import get_intent_service

        return SafetyEvaluator(
            chain=chain,
            intent_service=get_intent_service(),
            judge=judge,
        )

    raise ValueError(f"Unknown category: {category}")


def _build_chain() -> Any:
    """Load the FAISS index and build the RAG chain (cached)."""
    from medibot.services.retrieval import load_vectorstore

    return build_rag_chain(load_vectorstore())


def _selected_categories(categories: list[str] | None) -> list[str]:
    if categories:
        unknown = set(categories) - set(DATASET_FILES)
        if unknown:
            raise ValueError(f"Unknown categories: {sorted(unknown)}")
        return list(categories)
    return list(DATASET_FILES)


def run(
    *,
    categories: list[str] | None = None,
    limit: int | None = None,
    case_id: str | None = None,
    save_db: bool = True,
    report_dir: Path | str | None = None,
    sleep_seconds: float = 0.5,
    chain: Any | None = None,
    vectorstore: Any | None = None,
    judge: LLMJudge | None = None,
) -> dict[str, Any]:
    """Run evaluation over the selected categories and persist a report.

    Returns a summary dict with overall score, pass rate, and per-category
    aggregates.  Supports group filters (``limit`` / ``case_id``) and DB +
    JSON reporting.
    """
    start = time.perf_counter()
    categories = _selected_categories(categories)

    if chain is None and any(c != "retrieval" for c in categories):
        chain = _build_chain()

    outcomes: list[CaseOutcome] = []
    for category in categories:
        evaluator = build_evaluator(category, chain=chain, vectorstore=vectorstore, judge=judge)
        cases = load_cases(category)
        if case_id is not None:
            cases = [c for c in cases if c["id"] == case_id]
            if not cases:
                raise ValueError(f"Case not found: {category}/{case_id}")
        if limit is not None:
            cases = cases[:limit]
        for case in cases:
            outcome = evaluator.evaluate(case)
            outcomes.append(outcome)
            logger.info(
                "case=%s category=%s passed=%s score=%.1f",
                outcome.case_id,
                outcome.category,
                outcome.passed,
                outcome.score,
            )
            if sleep_seconds > 0 and category != "retrieval":
                time.sleep(sleep_seconds)

    duration_ms = round((time.perf_counter() - start) * 1000, 1)
    report = _aggregate(outcomes, categories, duration_ms)

    if report_dir is not None or save_db:
        report_path = None
        if report_dir is not None:
            report_path = _write_report(report, report_dir)
            report["report_path"] = report_path
        if save_db:
            _save_run(report, outcomes, report_path)

    _print_summary(report, outcomes)
    return report


def _aggregate(
    outcomes: list[CaseOutcome],
    categories: list[str],
    duration_ms: float,
) -> dict[str, Any]:
    """Compute overall and per-category aggregates."""
    by_category: dict[str, list[CaseOutcome]] = {}
    for outcome in outcomes:
        by_category.setdefault(outcome.category, []).append(outcome)

    category_scores: dict[str, dict[str, Any]] = {}
    for category in categories:
        rows = by_category.get(category, [])
        if not rows:
            continue
        avg = sum(o.score for o in rows) / len(rows)
        passed = sum(1 for o in rows if o.passed)
        category_scores[category] = {
            "score": round(avg, 2),
            "pass_rate": round(passed / len(rows), 3),
            "passed": passed,
            "total": len(rows),
        }

    overall = sum(o.score for o in outcomes) / len(outcomes) if outcomes else 0.0
    overall_pass_rate = (
        sum(1 for o in outcomes if o.passed) / len(outcomes) if outcomes else 0.0
    )

    return {
        "status": "completed",
        "overall_score": round(overall, 2),
        "overall_pass_rate": round(overall_pass_rate, 3),
        "categories": categories,
        "category_scores": category_scores,
        "case_count": len(outcomes),
        "duration_ms": duration_ms,
    }


def _write_report(report: dict[str, Any], report_dir: Path | str | None) -> str:
    """Persist the aggregated report as JSON and return its path."""
    directory = Path(report_dir or DEFAULT_REPORT_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    path = directory / f"evaluation-{timestamp}.json"
    payload = {**report, "written_at": timestamp}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Report written to %s", path)
    return str(path)


def _save_run(
    report: dict[str, Any],
    outcomes: list[CaseOutcome],
    report_path: str | None,
) -> int:
    """Persist an EvaluationRun + case results to SQLite."""
    init_db()
    db = SessionLocal()
    try:
        run_row = EvaluationRun(
            status=report["status"],
            overall_score=report["overall_score"],
            overall_pass_rate=report["overall_pass_rate"],
            categories=report["categories"],
            category_scores=report["category_scores"],
            case_count=report["case_count"],
            duration_ms=report["duration_ms"],
            report_path=report_path,
        )
        db.add(run_row)
        db.flush()
        for outcome in outcomes:
            db.add(
                EvaluationCaseResult(
                    run_id=run_row.id,
                    case_id=outcome.case_id,
                    category=outcome.category,
                    passed=outcome.passed,
                    score=outcome.score,
                    sub_scores=outcome.sub_scores,
                    reasoning=outcome.reasoning,
                    details=outcome.details,
                )
            )
        db.commit()
        run_id = run_row.id
    finally:
        db.close()
    logger.info("Evaluation run #%d saved to SQLite", run_id if "run_id" in locals() else -1)
    return run_id if "run_id" in locals() else -1


def _print_summary(report: dict[str, Any], outcomes: list[CaseOutcome]) -> None:
    """Print a human-readable summary table."""
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"Overall score:     {report['overall_score']:.1f}/10")
    print(f"Overall pass rate: {report['overall_pass_rate']:.0%}")
    print(f"Cases evaluated:   {report['case_count']}")
    print(f"Duration:          {report['duration_ms']} ms")
    print("-" * 60)
    print(f"{'Category':<12} {'Score':>6} {'Pass':>6} {'Total':>6}")
    print("-" * 60)
    for category, stats in report["category_scores"].items():
        print(f"{category:<12} {stats['score']:>6.1f} {stats['passed']:>6}/{stats['total']:<6}")
    print("-" * 60)
    for outcome in outcomes:
        marker = "PASS" if outcome.passed else "FAIL"
        print(f"  [{marker}] {outcome.category}/{outcome.case_id} — {outcome.reasoning}")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for ``medibot evaluate``."""
    parser = argparse.ArgumentParser(
        prog="medibot evaluate",
        description="Run the MediBot evaluation suite.",
    )
    parser.add_argument(
        "--category",
        action="append",
        choices=sorted(DATASET_FILES),
        help="Category to evaluate (repeatable; default: all).",
    )
    parser.add_argument("--limit", type=int, help="Limit cases per category.")
    parser.add_argument("--case-id", help="Run a single case by id.")
    parser.add_argument(
        "--report-dir",
        type=str,
        help="Directory for JSON reports (default: reports/).",
    )
    parser.add_argument(
        "--no-save-db",
        action="store_true",
        help="Do not persist the run to SQLite.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Seconds to sleep between LLM-judged cases (default: 0.5).",
    )
    args = parser.parse_args(argv)

    report_dir = args.report_dir or DEFAULT_REPORT_DIR
    run(
        categories=args.category,
        limit=args.limit,
        case_id=args.case_id,
        save_db=not args.no_save_db,
        report_dir=report_dir,
        sleep_seconds=args.sleep,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
