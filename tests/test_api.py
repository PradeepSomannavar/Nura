"""Smoke tests for the FastAPI application layer and services."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from medibot.core.database import Base, get_db
from medibot.main import app


def _override_db():
    """Point the app's DB dependency at a fresh in-memory SQLite.

    Uses a single shared connection (``StaticPool``) so every session sees
    the tables created on the same in-memory database.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return app


def test_health():
    """Health endpoint responds ok."""
    client = TestClient(app)
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_analytics_empty():
    """Analytics returns an empty snapshot on startup."""
    client = TestClient(_override_db())
    r = client.get("/api/analytics")
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_create_session_and_list_messages():
    """Sessions can be created and their (empty) messages listed."""
    client = TestClient(_override_db())

    r = client.post("/api/sessions")
    assert r.status_code == 200
    session_id = r.json()["session_id"]
    assert session_id > 0

    r = client.get(f"/api/sessions/{session_id}/messages")
    assert r.status_code == 200
    assert r.json() == []


def test_missing_session_returns_404():
    """Listing messages for a missing session returns 404."""
    client = TestClient(_override_db())
    r = client.get("/api/sessions/9999/messages")
    assert r.status_code == 404
