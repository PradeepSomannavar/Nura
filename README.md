<div align="center">

# 🩺 MediBot — RAG-based Clinical Reference Assistant

Context-aware Q&A over a local medical knowledge base using FAISS vector search + Groq LLM.

</div>

## 🧠 Overview

A modular, production-ready Retrieval-Augmented Generation (RAG) pipeline. Instead of hallucinating, the LLM answers are constrained by retrieved passages from a FAISS vector store built from your PDF documents.

## ✨ Key Features

- **FAISS vector store** for fast semantic retrieval
- **SentenceTransformer embeddings** (`all-MiniLM-L6-v2`) — configurable via env vars
- **Groq LLM backend** with configurable model and parameters
- **Source document traceability** — shows which chunks supported each answer
- **Streamlit chat UI** with cached vector store and conversation history
- **CLI mode** for quick queries without a browser
- **Environment-driven config** — tune chunking, retrieval, and LLM params via `.env`

## 🏗 Architecture

```
PDF(s) ──► Text Splitter ──► Embeddings ──► FAISS Index (vectorstore/db_faiss)
                                              │
User Query ──► Retriever (top-k) ─────────────┘
                 │
             Prompt Assembly
                 │
             LLM Generation (Groq)
                 │
             Answer + Source Chunks
```

### Project Structure

```
src/medibot/
├── __init__.py        # Package metadata
├── config.py          # Centralized configuration (env-driven)
├── embeddings.py      # Embedding model factory
├── vectorstore.py     # FAISS load/build operations
├── ingestion.py       # PDF loading and text chunking
├── llm.py             # LLM init and RAG chain builder
├── cli.py             # CLI entry point (ingest / query / web)
└── app.py             # Streamlit web interface
tests/                 # Unit and integration tests
legacy/                # Original scripts (preserved for reference)
```

## 🔐 Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```
GROQ_API_KEY=groq_xxxxxxxxxxxxxxxxxxx
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxx   # optional, for HF embedding API
```

Optional tuning variables:

```
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
GROQ_MODEL=llama-3.1-8b-instant
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RETRIEVER_K=3
LLM_TEMPERATURE=0.5
LLM_MAX_TOKENS=512
```

## ⚙️ Installation

### Using uv (recommended)

```zsh
uv sync
uv sync --extra dev   # includes pytest + ruff
```

### Using pip

```zsh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 🚀 Usage

### Build the vector store (one-time)

```zsh
uv run medibot ingest
```

### Interactive CLI

```zsh
uv run medibot query
```

### Streamlit Web App

```zsh
uv run medibot web
```

Open the URL shown (default: http://localhost:8501) and start chatting.

## 🧪 Testing

```zsh
uv run pytest tests/ -v
uv run ruff check src/ tests/
```

## 🐛 Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `FAISS index not found` | Vector store not built | Run `medibot ingest` first |
| Empty / irrelevant answers | Too small `k` or chunk mismatch | Set `RETRIEVER_K=5` or adjust `CHUNK_SIZE` |
| Hallucinations | LLM ignoring context | Tighten prompt, lower temperature |
| `GROQ_API_KEY not set` | Missing env var | Add to `.env` file |

## ⚖️ Disclaimer

This tool is for **educational and reference purposes only**. It does **not** provide medical advice, diagnosis, or treatment recommendations. Always consult a licensed healthcare professional for medical decisions.
