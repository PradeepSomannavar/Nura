"""PDF ingestion pipeline (service layer).

Relocates the original ``medibot.ingestion`` logic into the services layer
while preserving the public ``load_pdfs`` / ``chunk_documents`` names.
"""

from __future__ import annotations

import logging

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from medibot.core.config import settings

logger = logging.getLogger(__name__)


def load_pdfs(data_path: str | None = None) -> list[Document]:
    """Load all PDFs from a directory."""
    path = data_path or settings.DATA_PATH
    logger.info("Loading PDFs from %s", path)
    loader = DirectoryLoader(path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    logger.info("Loaded %d pages from PDFs", len(documents))
    return documents


def chunk_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """Split documents into overlapping text chunks."""
    size = chunk_size or settings.CHUNK_SIZE
    overlap = chunk_overlap if chunk_overlap is not None else settings.CHUNK_OVERLAP
    logger.info(
        "Splitting %d documents into chunks (size=%d, overlap=%d)",
        len(documents),
        size,
        overlap,
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info("Created %d text chunks", len(chunks))
    return chunks
