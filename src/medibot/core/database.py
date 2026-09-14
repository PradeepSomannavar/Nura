"""SQLAlchemy engine, session factory, and FastAPI dependency.

Provides a single ``engine`` / ``SessionLocal`` backed by SQLite, a
``Base`` declarative class for models, and a ``get_db()`` dependency for
FastAPI route handlers.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from medibot.core.config import settings


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def init_db() -> None:
    """Create all tables defined by ORM models (idempotent)."""
    from medibot import models  # noqa: F401  (register models on Base)

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
