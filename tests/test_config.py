"""Tests for MediBot configuration."""

from medibot.config import CHUNK_OVERLAP, CHUNK_SIZE, FAISS_INDEX_PATH, RETRIEVER_K


def test_config_defaults():
    """Config defaults are reasonable."""
    assert CHUNK_SIZE > 0
    assert CHUNK_OVERLAP >= 0
    assert CHUNK_OVERLAP < CHUNK_SIZE
    assert RETRIEVER_K > 0
    assert "vectorstore" in FAISS_INDEX_PATH
