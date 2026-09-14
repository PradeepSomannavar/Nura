"""Streamlit dashboard for MediBot evaluation runs.

Launch with:  uv run streamlit run src/medibot/evaluation/dashboard/dashboard.py
"""

from __future__ import annotations

import csv
import io
import json

import streamlit as st
from sqlalchemy import select

from medibot.core.database import SessionLocal, init_db
from medibot.models.evaluation import EvaluationCaseResult, EvaluationRun

st.set_page_config(page_title="MediBot — Evaluation Dashboard", layout="wide")


@st.cache_resource
def _get_db():
    init_db()
    return SessionLocal()


def load_runs() -> list[EvaluationRun]:
    """Load all evaluation runs, newest first."""
    db = _get_db()
    with db:
        return list(db.execute(select(EvaluationRun).order_by(EvaluationRun.id.desc())).scalars())


def load_results(run_id: int) -> list[EvaluationCaseResult]:
    """Load case results for a run."""
    db = _get_db()
    with db:
        return list(
            db.execute(
                select(EvaluationCaseResult).where(EvaluationCaseResult.run_id == run_id)
            ).scalars()
        )


def render_kpis(run: EvaluationRun) -> None:
    """Render the KPI row for a run."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Score", f"{run.overall_score or 0.0}/10")
    c2.metric("Pass Rate", f"{(run.overall_pass_rate or 0.0):.0%}")
    c3.metric("Cases", run.case_count)
    c4.metric("Duration", f"{run.duration_ms} ms")


def render_categories(run: EvaluationRun) -> None:
    """Render per-category score bars."""
    st.subheader("Category Breakdown")
    scores = run.category_scores or {}
    if not scores:
        st.info("No category scores recorded for this run.")
        return
    for category, stats in scores.items():
        score = stats.get("score", 0.0)
        passed = stats.get("passed", 0)
        total = stats.get("total", 0)
        st.progress(score / 10.0, text=f"{category}: {score}/10 ({passed}/{total} passed)")


def render_trend(runs: list[EvaluationRun]) -> None:
    """Render the overall-score trend over runs."""
    st.subheader("Score Trend")
    if len(runs) < 2:
        st.info("Run at least two evaluations to see a trend.")
        return

    data = [
        {
            "run": r.id,
            "overall_score": r.overall_score or 0.0,
            "pass_rate": r.overall_pass_rate or 0.0,
        }
        for r in reversed(runs)
    ]
    st.line_chart(data, x="run")


def render_failures(results: list[EvaluationCaseResult]) -> None:
    """Render a diagnostics table of failed cases."""
    st.subheader("Failed Case Diagnostics")
    failures = [r for r in results if not r.passed]
    if not failures:
        st.success("All cases passed.")
        return
    st.dataframe(
        [
            {
                "Case": r.case_id,
                "Category": r.category,
                "Score": r.score,
                "Reasoning": r.reasoning or "",
            }
            for r in failures
        ],
        use_container_width=True,
    )


def export_buttons(results: list[EvaluationCaseResult]) -> None:
    """Provide CSV and JSON export of the run's results."""
    st.subheader("Export")
    records = [
        {
            "case_id": r.case_id,
            "category": r.category,
            "passed": r.passed,
            "score": r.score,
            "sub_scores": json.dumps(r.sub_scores),
            "reasoning": r.reasoning or "",
        }
        for r in results
    ]

    csv_buffer = io.StringIO()
    if records:
        writer = csv.DictWriter(csv_buffer, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    st.download_button(
        "Download CSV",
        data=csv_buffer.getvalue(),
        file_name="evaluation_results.csv",
        mime="text/csv",
    )

    json_buffer = json.dumps(records, indent=2)
    st.download_button(
        "Download JSON",
        data=json_buffer,
        file_name="evaluation_results.json",
        mime="application/json",
    )


def main() -> None:
    """Render the evaluation dashboard."""
    st.title("MediBot Evaluation Dashboard")

    runs = load_runs()
    if not runs:
        st.info("No evaluation runs found. Run `medibot evaluate` first.")
        return

    render_trend(runs)

    run_ids = [r.id for r in runs]
    selected = st.selectbox("Select evaluation run", run_ids)
    run = next(r for r in runs if r.id == selected)

    render_kpis(run)
    render_categories(run)

    results = load_results(run.id)
    render_failures(results)
    export_buttons(results)


if __name__ == "__main__":
    main()
