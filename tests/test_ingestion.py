"""Tests for MediBot ingestion pipeline."""

from medibot.ingestion import chunk_documents


def test_chunk_documents():
    """Chunking should split documents into expected number of chunks."""
    from langchain_core.documents import Document

    doc = Document(page_content="word " * 2000, metadata={"source": "test.pdf"})
    chunks = chunk_documents([doc], chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    assert all(len(c.page_content) <= 550 for c in chunks)
