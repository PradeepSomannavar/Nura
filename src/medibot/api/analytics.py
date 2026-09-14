"""Analytics / metrics endpoints.

Phase 1 returns the in-memory metric snapshot for debugging.  A durable
analytics store and dashboard land in Phase 5.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from medibot.services.analytics import AnalyticsService, get_analytics_service

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics")
def analytics(
    service: AnalyticsService = Depends(get_analytics_service),
) -> dict:
    """Return the current in-memory request metrics snapshot."""
    return {"count": len(service.snapshot()), "metrics": service.snapshot()}
