# Functional Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| F-1 | Answer medical/health questions via RAG over the PDF corpus (FAISS, `all-MiniLM-L6-v2`) | ✅ |
| F-2 | Stream answers to the UI (SSE: `token / sources / done / error`; `meta` carries intent) | ✅ |
| F-3 | Multi-provider LLM: Gemini primary → Groq automatic fallback on failure | ✅ |
| F-4 | Domain guard: classify each message `MEDICAL_QUERY` / `NON_MEDICAL` / `HARMFUL_REQUEST`; refuse non-medical without running RAG | ✅ |
| F-5 | Hybrid memory: last 5 turns raw in prompt + rolling clinical summary persisted to SQLite | ✅ |
| F-6 | Persist chat sessions/messages/summaries (SQLite via SQLAlchemy) | ✅ |
| F-7 | CLI: `medibot ingest / query / evaluate / web` | ✅ |
| F-8 | HTTP backend: `/api/chat/stream`, `/api/health`, `/api/sessions`, `/api/analytics` | ✅ |
| F-9 | Evaluation framework: 5 categories (retrieval, accuracy, memory, citation, safety), LLM-as-a-Judge, dashboard | ✅ |
| F-10 | Medical-grade UI redesign (landing + chat) | 🔜 Phase 6 |
| F-11 | Programmatic `[n]` citations in answers (sources numbered in context) | ⚠️ Gap — see `07-learning/known-gaps.md` |

## Notes
- Prompts always live in `src/medibot/prompts/` as `.py` modules (never inline).
- Config centralized via `Settings` (`core/config.py`); secrets only in `.env`.