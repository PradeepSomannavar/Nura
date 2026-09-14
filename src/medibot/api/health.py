"""Health check endpoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from medibot.core.config import settings

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Health probe payload."""

    status: str = "ok"
    vectorstore_ready: bool
    vectorstore_path: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report service health and whether the vector index exists."""
    return HealthResponse(
        status="ok",
        vectorstore_ready=Path(settings.FAISS_INDEX_PATH).exists(),
        vectorstore_path=settings.FAISS_INDEX_PATH,
    )
