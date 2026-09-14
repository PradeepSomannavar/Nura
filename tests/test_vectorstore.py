"""Tests for the MediBot vector store service."""

from medibot.core.config import settings
from medibot.services.retrieval import load_vectorstore


def test_vectorstore_exists():
    """FAISS index directory should exist from prior build."""
    import os

    assert os.path.exists(settings.FAISS_INDEX_PATH)


def test_vectorstore_loads():
    """FAISS index should load without error."""
    db = load_vectorstore()
    assert db is not None


def test_vectorstore_search():
    """Similarity search should return results."""
    db = load_vectorstore()
    results = db.similarity_search("What is hypertension?", k=2)
    assert len(results) >= 1
    assert all(hasattr(r, "page_content") for r in results)
