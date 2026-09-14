# Implementation — Task Status

Tracking the 6-phase roadmap. Detail per phase lives in [`docs/phases/`](../phases/).

| Phase | Focus | Status | Evidence |
|-------|-------|--------|----------|
| 1 | FastAPI modular backend | ✅ Completed | Services/api/models/core layered; SSE chat; CLI works; `test_api/config/vectorstore/ingestion` |
| 2 | Gemini + Groq fallback | ✅ Completed | `FallbackChatModel`; provider tracked; `test_llm` |
| 3 | Intent guardrails | ✅ Completed | `INTENTS` enum + classifier (LLM + keyword fallback); refusal stream; non-medical skips RAG; `test_intent` (14) |
| 4 | Hybrid memory | ✅ Completed | `HybridMemory` + rolling summary SQLite; `test_memory` (5); live 7-turn verify |
| 5 | Evaluation framework | ✅ Completed | Runner + 5 evaluators + LLM judge + dashboard; `test_evaluation*` (19); live benchmark + DB |
| 6 | UI redesign | 🔜 Next | Nothing shipped yet |

## Phase deliverable files (implemented)
- P1: `api/*.py`, `core/*.py`, `models/*.py`, `schemas/chat.py`, `services/*.py`, `prompts/*.py`, `cli.py`, `main.py`
- P2: `services/llm.py` (fallback router)
- P3: `services/intent.py`, `prompts/intent.py`, `services/chat.py` wiring
- P4: `services/memory.py`, `services/summarizer.py`, `prompts/memory.py`, `models/memory.py`
- P5: `evaluation/` package (runner/evaluators/judges/metrics/datasets/dashboard), `models/evaluation.py`, `prompts/judge.py`

## Overdue / deferred (see also `07-learning/known-gaps.md`)
- Phase 4 §6 frontend memory wiring (refresh-restore) → Phase 6.
- Citation numbering in RAG context (F-11) — fixes accuracy of citation eval.
- `app.py` ruff cleanup (pre-existing) → Phase 6.
- `cache.py` / `analytics.py` stubs → when Redis/analytics phases are adopted.