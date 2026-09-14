"""Persistence models for evaluation runs (Phase 5)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from medibot.core.database import Base


class EvaluationRun(Base):
    """A single evaluation run (one CLI invocation)."""

    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(16), default="completed")
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_pass_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    categories: Mapped[list] = mapped_column(JSON, default=list)
    category_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    report_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    results: Mapped[list[EvaluationCaseResult]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class EvaluationCaseResult(Base):
    """Outcome for a single evaluation case within a run."""

    __tablename__ = "evaluation_case_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        ForeignKey("evaluation_runs.id", ondelete="CASCADE"), index=True
    )
    case_id: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(64), index=True)
    passed: Mapped[bool] = mapped_column()
    score: Mapped[float] = mapped_column(Float, default=0.0)
    sub_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    run: Mapped[EvaluationRun] = relationship(back_populates="results")
