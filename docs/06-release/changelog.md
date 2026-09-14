# Changelog

## Unreleased / in-progress
- **Phase 6 — UI redesign** (medical-grade landing + chat; backend verified).

## 2026-09-13 — Phases 1–5 complete
### Phase 1 — FastAPI modular backend
- Layered `src/medibot/` (api/core/models/schemas/prompts/services); Pydantic `Settings`; SQLAlchemy+SQLite; SSE chat; CLI (`ingest/query/web`).

### Phase 2 — Multi-provider LLM
- `FallbackChatModel` Gemini→Groq with provider tracking; `clean_stream_prefixes`; Gemini safety settings.
- Models: `gemini-2.5-flash` → `gemini-3.6-flash`; `llama-3.1-8b-instant` → `openai/gpt-oss-20b` (both retired by providers).

### Phase 3 — Intent guardrails
- `IntentService` (MEDICAL/NON_MEDICAL/HARMFUL) with LLM classifier + keyword fallback; refusal stream; wire into chat (non-medical skips RAG); `meta` event.

### Phase 4 — Hybrid memory
- `HybridMemory`: 5-turn buffer + rolling clinical summary persisted to SQLite (evict + summarize on overflow); session-scoped.

### Phase 5 — Evaluation framework
- `evaluation/` package: runner CLI, 5 evaluators, LLM judge, retrieval metrics, 15-case datasets, Streamlit dashboard; run history in `medibot.db`.
- First live benchmark (run 3): overall 6.1 (see `05-evaluation/results/2026-09-13.md`).

### Tooling / infra
- Test suite grown to **56 passing**; ruff clean (except `app.py`).
- Eval reports to `reports/` (gitignored).

## Known-backlog (tracked in `07-learning/known-gaps.md`)
- [G1] Citation numbering in RAG context (F-11).
- [G2] `app.py` ruff cleanup + UI redesign (Phase 6).
- [G3] Frontend memory restore wiring (Phase 4 §6).
- [G4] `cache.py` / `analytics.py` stubs → adopted in future phases.
- [G5] Judge: empty answers should fail-by-error.