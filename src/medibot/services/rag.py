"""RAG chain construction (service layer).

Builds the history-aware retrieval chain used by the API and CLI.  All
prompt templates come from ``medibot.prompts``; the LLM comes from
``medibot.services.llm`` with Gemini→Groq fallback.
"""

from __future__ import annotations

import logging

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.vectorstores import VectorStore

from medibot.core.config import settings
from medibot.prompts.contextualize import CONTEXTUALIZE_Q_PROMPT
from medibot.prompts.qa import QA_PROMPT
from medibot.services.llm import get_llm

logger = logging.getLogger(__name__)


def build_rag_chain(vectorstore: VectorStore, k: int | None = None) -> object:
    """Build the full RAG retrieval chain with conversation history."""
    llm = get_llm()
    top_k = k or settings.RETRIEVER_K
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, CONTEXTUALIZE_Q_PROMPT
    )
    combine_docs_chain = create_stuff_documents_chain(llm, QA_PROMPT)
    rag_chain = create_retrieval_chain(history_aware_retriever, combine_docs_chain)

    logger.info("RAG chain built with history support (k=%d)", top_k)
    return rag_chain
