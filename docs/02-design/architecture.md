# Architecture

See [`ARCHITECTURE.md`](../../ARCHITECTURE.md) for the full diagram and layered file tree.

## Layer Summary

```
Streamlit app.py (current UI)
       ↓ direct import
┌──────────────────────────────────────────────────┐
│  api/          FastAPI routers (SSE + REST)       │
│  schemas/      Pydantic DTOs (ChatRequest etc.)   │
├──────────────────────────────────────────────────┤
│  services/     Business logic                     │
│    chat.py     → answer_stream (intent → RAG)     │
│    intent.py   → IntentService + refusal_stream   │
│    memory.py   → HybridMemory (buffer + summary)  │
│    llm.py      → FallbackChatModel (Gemini→Groq)  │
│    rag.py      → build_rag_chain (FAISS + LLM)    │
│    retrieval.py, embeddings.py, summarizer.py     │
├──────────────────────────────────────────────────┤
│  core/         Config, database, logging          │
│  models/       SQLAlchemy ORM (sessions, msgs)    │
│  prompts/      Prompt modules (qa, intent, etc.)  │
├──────────────────────────────────────────────────┤
│  evaluation/   Runner, judges, evaluators, DB     │
│  dashboard/    Streamlit eval analytics           │
└──────────────────────────────────────────────────┘
```

## External dependencies
- **FAISS** — vector similarity search (ingested PDF corpus)
- **SQLite** (SQLAlchemy) — chat persistence + eval run history
- **Gemini** (`gemini-3.6-flash`) primary LLM · **Groq** (`openai/gpt-oss-20b`) fallback
- **Sentence-Transformers** (`all-MiniLM-L6-v2`) — local embeddings

## Key files
- `services/chat.py` — orchestrates intent guard → memory → RAG → SSE events
- `services/llm.py` — `FallbackChatModel`, `_configured_providers()`, `clean_stream_prefixes`
- `services/memory.py` — `HybridMemory`, eviction, DB load
- `services/rag.py` — `build_rag_chain`, `create_retrieval_chain` + history-aware retriever
- `core/config.py` — `Settings` (Pydantic BaseSettings), `PROJECT_ROOT`