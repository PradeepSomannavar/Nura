"""FastAPI application factory for Nura.

Registers routers, starts the database on startup, and wires in a health
probe.  The streamlit/CLI entry points continue to import the service layer
directly; this module is the HTTP backend.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from medibot.api import analytics_router, chat_router, health_router, memory_router
from medibot.core.config import settings
from medibot.core.database import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup; tear down on shutdown."""
    logger.info("Initializing database (%s)", settings.DATABASE_URL)
    init_db()
    logger.info("Database initialized")
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="Nura API",
        description="RAG-based clinical reference assistant",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(memory_router)
    app.include_router(analytics_router)

    return app


app = create_app()
