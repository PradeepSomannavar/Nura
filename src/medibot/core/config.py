"""Centralized configuration for MediBot (Pydantic BaseSettings).

All environment-driven settings flow through the singleton ``settings``
instance.  No other module should read environment variables directly.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Embeddings / retrieval ----
    EMBEDDING_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    FAISS_INDEX_PATH: str = Field(default=str(PROJECT_ROOT / "vectorstore" / "db_faiss"))
    DATA_PATH: str = Field(default=str(PROJECT_ROOT / "data"))
    RETRIEVER_K: int = Field(default=5)
    CHUNK_SIZE: int = Field(default=1000)
    CHUNK_OVERLAP: int = Field(default=150)

    # ---- LLM: Gemini (primary) + Groq (fallback) ----
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-3.6-flash")
    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = Field(default="openai/gpt-oss-20b")
    LLM_TEMPERATURE: float = Field(default=0.3)
    LLM_MAX_TOKENS: int = Field(default=512)
    ENABLE_STREAMING: bool = Field(default=True)

    # ---- Memory (Phase 4: hybrid buffer + summary) ----
    MEMORY_BUFFER_TURNS: int = Field(default=5)
    MEMORY_SUMMARY_STORE: str = Field(default="sqlite")

    # ---- Domain guardrails (Phase 3) ----
    ENABLE_INTENT_GUARD: bool = Field(default=True)

    # ---- Database / persistence ----
    DATABASE_URL: str = Field(default="sqlite:///./medibot.db")

    # ---- Hugging Face (optional) ----
    HF_TOKEN: str = Field(default="")
    HUGGINGFACE_REPO_ID: str = Field(default="mistralai/Mistral-7B-Instruct-v0.3")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()


settings = get_settings()
