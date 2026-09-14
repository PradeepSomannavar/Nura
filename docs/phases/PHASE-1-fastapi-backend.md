# Phase 1 — FastAPI Modular Backend Refactor

**Status:** Completed
**Dependencies:** None
**Skills to load:** `medibot-architecture`

## Objective

Refactor the current single-file Streamlit app + plain modules into a **modular, service-oriented FastAPI backend** with clean layer separation (api / core / models / schemas / services), while preserving/reusing the existing RAG logic (ingestion, vectorstore, embeddings, llm).

## Scope

- Introduce FastAPI as the backend (SSE streaming chat, health, memory, analytics endpoints).
- Restructure `src/medibot/` into layered directories per the architecture skill.
- Centralize config into Pydantic `BaseSettings`.
- Keep Streamlit as an optional frontend/consumer, OR move toward a SPA + FastAPI. (Confirm direction in Phase kickoff.)
- Add dependency injection via `Depends()`.

## In-Depth Todos

### 1. Restructure package layout
- [ ] Create layered structure under `src/medibot/`:
  - `api/` (routers: `health.py`, `chat.py`, `memory.py`, `analytics.py`)
  - `core/` (`config.py` [Pydantic], `database.py`, `logging.py`)
  - `models/` (SQLAlchemy persistence schemas)
  - `schemas/` (Pydantic DTOs)
  - `prompts/` (all prompt templates as `.py` modules — NOT inline in code)
  - `services/` (`llm.py`, `retrieval.py`, `embeddings.py`, `memory.py`, `cache.py`, `intent.py`, `analytics.py`)
  - `main.py` (FastAPI app factory)
- [ ] Move existing modules into matching services (reuse logic, don't rewrite).
- [ ] Add `__init__.py` to each new package.

### 1b. Prompts → dedicated `prompts/` package
- [ ] Create `src/medibot/prompts/` containing all prompt templates as separate `.py` files (e.g. `system.py`, `contextualize.py`, `qa.py`, `intent.py`, `memory.py`, `summary.py`, `judge.py`).
- [ ] Extract the current inline prompts from `llm.py` (`MEDICAL_SYSTEM_PROMPT`, `CONTEXTUALIZE_Q_SYSTEM`, and the `ChatPromptTemplate`s) into the `prompts/` package.
- [ ] Each prompt module exposes constants/templates imported by the service layer — **never** inline prompt strings in route/service code.
- [ ] Keep the raw prompt text constants (e.g. `MEDICAL_SYSTEM_PROMPT`) exported so templates remain versionable and reviewable without touching service logic.

### 2. Config → Pydantic BaseSettings
- [ ] Replace module-level `os.getenv` constants in `config.py` with a `Settings` class (env-driven, `extra="ignore"`).
- [ ] Export a singleton `settings = Settings()`.
- [ ] Update all importers to use `settings.X`.
- [ ] Add new settings: `GEMINI_API_KEY`, `GEMINI_MODEL_NAME`, `MEMORY_BUFFER_TURNS`, cache settings (phase-4/5 ready).

### 3. Database & persistence layer
- [ ] Add SQLite (via SQLAlchemy) `core/database.py`: `engine`, `SessionLocal`, `Base`, `get_db()` dependency.
- [ ] Add `models/memory.py`: `ChatSession`, `ChatMessage`, `ConversationSummary`, (optional `UserProfile`).
- [ ] Add `models/evaluation.py` hooks for later evaluation phase.
- [ ] `Base.metadata.create_all(bind=engine)` on startup.
- [ ] Move hybrid memory summary persistence to DB (or keep .py file — decide; DB recommended).

### 4. FastAPI app factory & routers
- [ ] `main.py`: create `FastAPI`, register routers, CORS, startup (init DB, build vectorstore lazily), health probe.
- [ ] `api/health.py`: `/api/health` returns status + vectorstore ready flag.
- [ ] `api/chat.py`: SSE streaming endpoint (`/api/chat/stream`) reusing the existing RAG chain + memory service.
- [ ] `api/memory.py`: read/write conversation memory endpoints.
- [ ] `api/analytics.py`: metrics endpoints (gated on later analytics phase; stub now).
- [ ] Keep route handlers **thin** — delegate to services.

### 5. Services layer extraction
- [ ] `services/llm.py`: keep `get_llm()`; prepare for multi-provider (phase 4) by exposing a provider router stub.
- [ ] `services/retrieval.py`: wrap vectorstore + hybrid retrieval (reuse `vectorstore.py`, `ingestion.py` logic).
- [ ] `services/embeddings.py`: `get_embedding_model()` factory (already exists — relocate).
- [ ] `services/memory.py`: `HybridMemory` service (buffer + summary), DB-backed.
- [ ] `services/cache.py`: interface + NoOp impl (Redis impl later phase).
- [ ] `services/intent.py`: stub for guardrails (phase 3).
- [ ] `services/analytics.py`: stub metrics accumulator.

### 6. CLI & Streamlit adaptation
- [ ] Keep `cli.py` working: `medibot ingest/query/web` should still function against the refactor.
- [ ] Decide: Streamlit `app.py` calls the FastAPI service layer directly (same process) OR talks over HTTP to FastAPI. Simpler MVP: import services directly; later separate.
- [ ] Update `pyproject.toml` with new deps: `fastapi`, `uvicorn`, `sse-starlette`, `sqlalchemy`, `pydantic-settings`.

### 7. Tests
- [ ] Ensure existing `tests/` still pass.
- [ ] Add config settings test, database session test, service-level smoke tests.

### 8. Verification
- [ ] `uv run ruff check src/ tests/`
- [ ] `uv run pytest tests/ -v`
- [ ] `uv run uvicorn medibot.main:app --reload` boots without error.
- [ ] `/api/health` responds.
- [ ] `uv run medibot web` still launches UI.
- [ ] Streaming chat works via the new service layer.

## Definition of Done

- Layered service-oriented FastAPI structure in place.
- Config centralized via `Settings`.
- Route handlers thin; business logic in services.
- SQLite persistence for chat/memory.
- Existing RAG functionality preserved and accessible through services.
- All tests pass, ruff clean.
