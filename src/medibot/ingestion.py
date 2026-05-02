"""PDF ingestion pipeline for MediBot."""

import logging

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_core.documents import Document

from medibot.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_PATH

logger = logging.getLogger(__name__)


def load_pdfs(data_path: str = DATA_PATH) -> list[Document]:
    """Load all PDFs from a directory."""
    logger.info("Loading PDFs from %s", data_path)
    loader = DirectoryLoader(
        data_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader,
    )
    documents = loader.load()
    logger.info("Loaded %d pages from PDFs", len(documents))
    return documents


def chunk_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Split documents into overlapping text chunks."""
    logger.info(
        "Splitting %d documents into chunks (size=%d, overlap=%d)",
        len(documents),
        chunk_size,
        chunk_overlap,
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    logger.info("Created %d text chunks", len(chunks))
    return chunks
