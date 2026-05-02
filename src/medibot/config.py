"""Centralized configuration for MediBot."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

FAISS_INDEX_PATH = os.getenv(
    "FAISS_INDEX_PATH",
    str(PROJECT_ROOT / "vectorstore" / "db_faiss"),
)

DATA_PATH = os.getenv(
    "DATA_PATH",
    str(PROJECT_ROOT / "data"),
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

HF_TOKEN = os.getenv("HF_TOKEN", "")
HUGGINGFACE_REPO_ID = os.getenv(
    "HUGGINGFACE_REPO_ID",
    "mistralai/Mistral-7B-Instruct-v0.3",
)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "5"))

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "512"))
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "false").lower() == "true"
