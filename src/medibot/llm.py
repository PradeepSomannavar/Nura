"""LLM and RAG chain setup for MediBot."""

import logging

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.vectorstores import VectorStore
from langchain_groq import ChatGroq

from medibot.config import (
    ENABLE_STREAMING,
    GROQ_API_KEY,
    GROQ_MODEL_NAME,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    RETRIEVER_K,
)

logger = logging.getLogger(__name__)

MEDICAL_SYSTEM_PROMPT = """You are MediBot, an advanced AI medical reference assistant.

RESPONSE GUIDELINES:
1. Always answer the user's question directly and completely
2. Use the provided medical context as your primary source
3. If the context is incomplete, supplement with general medical knowledge
4. Structure answers clearly with headings, bullet points, or numbered lists
5. Be precise with medical terminology but explain complex terms
6. Include relevant info: symptoms, causes, diagnosis, treatment, prognosis
7. When you use information from a specific source document, reference it with [1], [2], etc.
8. ALWAYS end with a brief disclaimer that this is for reference only, not medical advice.

Context:
{context}"""

CONTEXTUALIZE_Q_SYSTEM = (
    "Given a chat history and the latest user question which might reference context "
    "in the chat history, formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, just reformulate it if needed "
    "and otherwise return it as is."
)

CONTEXTUALIZE_Q_PROMPT = ChatPromptTemplate.from_messages([
    ("system", CONTEXTUALIZE_Q_SYSTEM),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", MEDICAL_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])


def get_llm(
    model_name: str = GROQ_MODEL_NAME,
    api_key: str = GROQ_API_KEY,
    temperature: float = LLM_TEMPERATURE,
    max_tokens: int = LLM_MAX_TOKENS,
) -> ChatGroq:
    """Initialize a Groq chat model."""
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")

    logger.info("Initializing Groq LLM: %s (streaming=%s)", model_name, ENABLE_STREAMING)
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
        streaming=ENABLE_STREAMING,
    )


def build_rag_chain(
    vectorstore: VectorStore,
    k: int = RETRIEVER_K,
) -> object:
    """Build the full RAG retrieval chain with conversation history."""
    llm = get_llm()
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    # 1. History-aware retriever (reformulates query based on history)
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, CONTEXTUALIZE_Q_PROMPT
    )

    # 2. Document combiner
    combine_docs_chain = create_stuff_documents_chain(llm, QA_PROMPT)

    # 3. Final RAG chain
    rag_chain = create_retrieval_chain(history_aware_retriever, combine_docs_chain)

    logger.info("Advanced RAG chain built with history support (k=%d)", k)
    return rag_chain
