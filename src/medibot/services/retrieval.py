"""Retrieval service wrapping the FAISS vector store.

Relocates the original ``medibot.vectorstore`` logic into the services layer
while preserving load/search behaviour.  Provides lazy loading so the index
is built once per process.
"""

from __future__ import annotations

import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from medibot.core.config import settings
from medibot.services.embeddings import get_embedding_model

logger = logging.getLogger(__name__)

_vectorstore: FAISS | None = None


def load_vectorstore(index_path: str | None = None) -> FAISS:
    """Load the persisted FAISS index (cached per process)."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    path = Path(index_path or settings.FAISS_INDEX_PATH)
    if not path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {path}. "
            "Run 'medibot ingest' first to build the vector store."
        )

    logger.info("Loading FAISS index from %s", path)
    db = FAISS.load_local(
        str(path),
        get_embedding_model(),
        allow_dangerous_deserialization=True,
    )
    _vectorstore = db
    return db


def build_and_save_vectorstore(
    documents: list[Document],
    index_path: str | None = None,
) -> FAISS:
    """Create a FAISS index from documents and persist it to disk."""
    global _vectorstore
    path = index_path or settings.FAISS_INDEX_PATH
    logger.info("Building FAISS index from %d documents", len(documents))
    db = FAISS.from_documents(documents, get_embedding_model())
    db.save_local(path)
    _vectorstore = db
    logger.info("FAISS index saved to %s", path)
    return db


def get_vectorstore() -> FAISS:
    """Alias returning the loaded vector store (raises if missing)."""
    return load_vectorstore()


def similarity_search(
    query: str,
    k: int | None = None,
    index_path: str | None = None,
) -> list[Document]:
    """Run a similarity search over the vector store."""
    db = load_vectorstore(index_path)
    top_k = k or settings.RETRIEVER_K
    return db.similarity_search(query, k=top_k)
