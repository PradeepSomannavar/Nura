"""Business logic / orchestration layer for MediBot.

Services depend on core, models, schemas, and prompts — never on api/.
Route handlers (api/) depend on services, never the reverse.
"""

from medibot.services.analytics import AnalyticsService, RequestMetric, get_analytics_service
from medibot.services.cache import BaseCache, NoOpCache, get_cache_service
from medibot.services.embeddings import get_embedding_model
from medibot.services.ingestion import chunk_documents, load_pdfs
from medibot.services.intent import Intent, IntentService, classify_intent, get_intent_service
from medibot.services.llm import LLMProvider, clean_stream_prefixes, get_llm
from medibot.services.memory import HybridMemory, MemoryContext
from medibot.services.rag import build_rag_chain
from medibot.services.retrieval import (
    build_and_save_vectorstore,
    get_vectorstore,
    load_vectorstore,
    similarity_search,
)

__all__ = [
    "AnalyticsService",
    "BaseCache",
    "HybridMemory",
    "Intent",
    "IntentService",
    "LLMProvider",
    "MemoryContext",
    "NoOpCache",
    "RequestMetric",
    "build_and_save_vectorstore",
    "build_rag_chain",
    "chunk_documents",
    "classify_intent",
    "clean_stream_prefixes",
    "get_analytics_service",
    "get_cache_service",
    "get_embedding_model",
    "get_intent_service",
    "get_llm",
    "get_vectorstore",
    "load_pdfs",
    "load_vectorstore",
    "similarity_search",
]
