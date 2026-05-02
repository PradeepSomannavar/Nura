"""Embedding model factory for MediBot."""

import logging

from langchain_huggingface import HuggingFaceEmbeddings

from medibot.config import EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)


def get_embedding_model(model_name: str = EMBEDDING_MODEL_NAME) -> HuggingFaceEmbeddings:
    """Load a local sentence-transformer embedding model."""
    logger.info("Loading embedding model: %s", model_name)
    return HuggingFaceEmbeddings(model_name=model_name)
