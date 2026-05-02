"""FAISS vector store operations for MediBot."""

import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from medibot.config import FAISS_INDEX_PATH
from medibot.embeddings import get_embedding_model

logger = logging.getLogger(__name__)


def load_vectorstore(index_path: str = FAISS_INDEX_PATH) -> FAISS:
    """Load a persisted FAISS index from disk."""
    path = Path(index_path)
    if not path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {path}. "
            "Run 'medibot ingest' first to build the vector store."
        )

    logger.info("Loading FAISS index from %s", index_path)
    embeddings = get_embedding_model()
    db = FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return db


def build_and_save_vectorstore(
    documents: list[Document],
    index_path: str = FAISS_INDEX_PATH,
) -> FAISS:
    """Create a FAISS index from documents and persist it to disk."""
    logger.info("Building FAISS index from %d documents", len(documents))
    embeddings = get_embedding_model()
    db = FAISS.from_documents(documents, embeddings)
    db.save_local(index_path)
    logger.info("FAISS index saved to %s", index_path)
    return db
