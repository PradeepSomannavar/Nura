"""Tests for MediBot configuration."""

from medibot.core.config import get_settings, settings


def test_settings_defaults():
    """Settings defaults are reasonable."""
    assert settings.CHUNK_SIZE > 0
    assert settings.CHUNK_OVERLAP >= 0
    assert settings.CHUNK_OVERLAP < settings.CHUNK_SIZE
    assert settings.RETRIEVER_K > 0
    assert "vectorstore" in settings.FAISS_INDEX_PATH


def test_get_settings_singleton():
    """get_settings should return a cached singleton."""
    assert get_settings() is get_settings()
