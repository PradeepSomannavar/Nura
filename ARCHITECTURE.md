# MediBot Architecture

> **This document describes the TARGET architecture** — the modular, production-grade design we are evolving toward phases. Current code still lives in a flat `src/medibot/` layout with a Streamlit UI and inline prompts; the phased plan in [`docs/phases/README.md`](docs/phases/README.md) migrates it here incrementally.

- **Current codebase:** `/src/medibot/` flat modules + Streamlit `app.py`
- **Target:** Layered FastAPI backend + services + persistence + evaluation
- **Vertex doc lives at the repo root**; phase docs link back to it.

---

## 1. High-Level Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                          │
│                                                                     │
│    Streamlit / SPA  ──HTTP / SSE (Server-Sent Events)──▶  FastAPI  │
└──────────────────────────────────────────────────┬────────────────┘
                                                   │
┌──────────────────────────────────────────────────▼────────────────┐
│                       APPLICATION LAYER  (api/)                    │
│                                                                     │
│   routers:  chat.py   memory.py   analytics.py   health.py          │
│   • thin handlers  • Depends() DI  • Pydantic request/response     │
└──────────────────────────────────────────────────┬────────────────┘
                                                   │
┌──────────────────────────────────────────────────▼────────────────┐
│                            CORE LAYER                              │
│                                                                     │
│   config.py (Pydantic Settings)   database.py   logging.py          │
│   security / middleware                                             │
└──────────────────────────────────────────────────┬────────────────┘
                                                   │
┌──────────────────────────────────────────────────▼────────────────┐
│                         SERVICE LAYER                              │
│                                                                     │
│   llm.py (Gemini → Groq router)   retrieval.py   embeddings.py      │
│   intent.py (guardrails)          memory.py (hybrid)               │
│   cache.py                        analytics.py                     │
│        │                               │              │            │
│        │            ┌──────────────────┼──────────────┼───┐        │
│        ▼            ▼                  ▼              ▼   ▼        │
│  ┌──────────┐  ┌──────────┐    ┌───────────┐   ┌───────────┐       │
│  │ PROMPTS  │  │  FAISS   │    │  SQLite   │   │  Redis    │       │
│  │ prompts/ │  │  index   │    │ memory/   │   │  cache    │       │
│  │ (.py)    │  │          │    │ logs/eval │   │           │       │
│  └──────────┘  └──────────┘    └───────────┘   └───────────┘       │
└───────────────────────────────────────────────────────────────────┘
                            │
                            ▼
        EVALUATION:  runner → LLM-as-a-Judge → SQLite history → dashboard
```

**Data flow (one chat turn):**

```
User msg → api/chat (SSE) → intent.py guardrail (medical only?)
        → memory.py (build buffer + summary context)
        → retrieval.py (hybrid search over FAISS)
        → llm.py (Gemini primary → Groq fallback)
        → compose answer (with citations) → stream to UI
        → analytics.py (log latency, provider, guardrail hits)
        → memory.py (append turn; evict to summary if > buffer)
```

---

## 2. File Structure (Target)

```
src/medibot/
├── __init__.py                 # version
├── main.py                     # FastAPI app factory + lifespan
│
├── api/                        # application layer — thin HTTP handlers
│   ├── __init__.py
│   ├── health.py               # /api/health
│   ├── chat.py                 # /api/chat/stream  (SSE)
│   ├── memory.py               # conversation memory endpoints
│   └── analytics.py            # metrics/dashboard endpoints
│
├── core/                       # cross-cutting infrastructure
│   ├── __init__.py
│   ├── config.py               # Pydantic BaseSettings (single source of truth)
│   ├── database.py             # SQLAlchemy engine, SessionLocal, get_db()
│   └── logging.py              # structured logging setup
│
├── models/                     # SQLAlchemy persistence models
│   ├── __init__.py
│   ├── session.py              # ChatSession, ChatMessage
│   ├── memory.py               # ConversationSummary (hybrid memory)
│   └── evaluation.py           # eval runs / results
│
├── schemas/                    # Pydantic DTOs (request/response)
│   ├── __init__.py
│   ├── chat.py
│   ├── memory.py
│   └── analytics.py
│
├── prompts/                    # ALL prompt templates — .py modules, never inline
│   ├── __init__.py
│   ├── contextualize.py        # history → standalone question
│   ├── qa.py                   # main RAG answer prompt (medical system)
│   ├── intent.py               # intent classification / domain guardrail
│   ├── memory.py               # memory-formatting prompts
│   ├── summary.py              # rolling conversation-summary prompt
│   └── judge.py                # LLM-as-a-Judge evaluation prompts
│
├── services/                   # business logic — framework-agnostic
│   ├── __init__.py
│   ├── llm.py                  # Gemini primary → Groq fallback router
│   ├── retrieval.py            # hybrid retrieval over vectorstore
│   ├── embeddings.py           # embedding model factory
│   ├── intent.py               # classifier + medical domain guardrails
│   ├── memory.py               # HybridMemory (buffer + summary)
│   ├── cache.py                # cache interface + NoOp/Redis impl
│   └── analytics.py            # metrics accumulator
│
├── evaluation/                 # production eval framework
│   ├── __init__.py
│   ├── runner.py               # batch eval runner + SQLite persistence
│   ├── judge.py                # LLM-as-a-Judge scoring
│   └── dataset.py              # eval queries / golden answers
│
├── cli.py                      # kept: medibot ingest/query/web
└── app.py                      # Streamlit UI (Phase 6 redesign target)
```

**Data / artifacts** (outside `src/`, gitignored as needed):
```
data/            # source PDFs (ingestion input)
vectorstore/     # persisted FAISS index (db_faiss)
medibot.db       # SQLite (memory, logs, eval history)
```

---

## 3. Key Points & Design Decisions

### 3.1 Prompt management — dedicated `prompts/` package
- All prompt templates live in `src/medibot/prompts/*.py` as named exports (constants / compiled `ChatPromptTemplate`s).
- **No inline prompt strings** in routes, services, or UI code.
- Motivations: versionable, reviewable, testable, reusable across providers, and swap-able without touching business logic.
- Current inline prompts in `llm.py` (`MEDICAL_SYSTEM_PROMPT`, `CONTEXTUALIZE_Q_SYSTEM`) are migrated into `prompts/qa.py` and `prompts/contextualize.py` in Phase 1.

### 3.2 LLM multi-provider (Gemini primary, Groq fallback)
- `services/llm.py` exposes a provider router: try Gemini; on failure/rate-limit fall back to Groq.
- Config-driven via `GEMINI_API_KEY` / `GEMINI_MODEL_NAME`, `GROQ_API_KEY` / `GROQ_MODEL_NAME`.
- Never log API keys/tokens.

### 3.3 Intent classification + domain guardrails
- Every user turn passes through `intent.py` before RAG.
- Off-topic / non-medical queries are rejected or redirected with a clear message.
- Guardrail results logged to analytics (helps tune sensitivity).

### 3.4 Hybrid memory (buffer + summary)
- **Buffer:** last 5 turns (10 messages) injected directly into the prompt.
- **Rolling summary:** older turns evicted into a compressed summary, persisted in SQLite (`ConversationSummary`).
- Both combined form the memory context for history-aware retrieval.

### 3.5 Retrieval
- FAISS vector index built from chunked PDFs (`ingestion.py` + `vectorstore.py` logic preserved in services).
- History-aware retriever reformulates queries using the memory context.
- `RETRIEVER_K` configurable.

### 3.6 Configuration
- All settings central in `core/config.py` via Pydantic `BaseSettings` (env-driven) — no scattered `os.getenv`.

### 3.7 Evaluation
- Production-grade framework: batch runner + LLM-as-a-Judge + golden dataset + results persisted in SQLite + dashboard endpoints.
- Replaces the current heuristic `evaluate.py` (keyword hit-rate + latency only).

### 3.8 UI redesign is the LAST phase
- Correctness, structure, security, and behavior come first.
- UI is redesigned only after the backend + features exist, so it can reflect real states (streaming, memory, citations, guardrail responses).

### 3.9 Security
- Secrets in `.env` (gitignored); never committed or logged.
- Medical content disclaimer is always included in system prompt output.

---

## 4. Current → Target Mapping

| Concern | Current (today) | Target (post-phases) |
|---|---|---|
| Server | Streamlit only | FastAPI (+ optional Streamlit/SPA client) |
| Config | `config.py` `os.getenv` constants | `core/config.py` Pydantic `Settings` |
| Prompts | inline in `llm.py` | `prompts/*.py` package |
| LLM | Groq only | Gemini → Groq fallback router |
| Memory | none (stateless) | Hybrid buffer + summary (SQLite) |
| Intent/guardrail | none | `services/intent.py` |
| Persistence | FAISS only | FAISS + SQLite + Redis (cache) |
| Eval | heuristic `evaluate.py` | LLM-as-a-Judge framework |
| UI | gradient premium theme | professional medical theme (Phase 6) |

---

## 5. Phase Roadmap Reference

See [`docs/phases/README.md`](docs/phases/README.md) for the ordered phase plan. UI redesign is **Phase 6 (last)**.

| Phase | Deliverable |
|---|---|
| 1 | FastAPI modular backend + `prompts/` + config + persistence |
| 2 | Gemini primary + Groq fallback |
| 3 | Intent classifier + domain guardrails |
| 4 | Hybrid memory (buffer + summary) |
| 5 | Production evaluation framework |
| 6 | Professional UI redesign (last) |
