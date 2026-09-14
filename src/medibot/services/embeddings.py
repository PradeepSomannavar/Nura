"""Embedding model factory (service layer).

Relocates the original ``medibot.embeddings`` logic into the services layer
while preserving the same public ``get_embedding_model`` name for imports.
"""

from __future__ import annotations

import logging

from langchain_huggingface import HuggingFaceEmbeddings

from medibot.core.config import settings

logger = logging.getLogger(__name__)


def get_embedding_model(
    model_name: str | None = None,
) -> HuggingFaceEmbeddings:
    """Load a local sentence-transformer embedding model."""
    name = model_name or settings.EMBEDDING_MODEL
    logger.info("Loading embedding model: %s", name)
    return HuggingFaceEmbeddings(model_name=name)
