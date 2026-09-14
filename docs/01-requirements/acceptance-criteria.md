# Acceptance Criteria

Mapping each capability to the concrete, testable acceptance condition.

| Requirement | Acceptance criterion | Evidence |
|-------------|----------------------|----------|
| RAG medical QA (F-1) | Given a medical query, answer grounded in retrieved context with relevance ≥ 7/10 | Accuracy eval 9.7/10 (3/3 pass) |
| SSE streaming (F-2) | `POST /api/chat/stream` emits `token`, `sources`, `meta`, `done` SSE events with `ChatStreamEvent` schema | Live verification; `api/chat.py` |
| Multi-provider fallback (F-3) | Break primary provider → answer still arrives within 120s via fallback | Live: Groq fallback confirmed when Gemini 429 |
| Domain refusal (F-4) | Non-medical message → `meta` event with `NON_MEDICAL` intent + refusal stream; RAG never called | `test_intent.py` (14 cases, incl. non-medical skips RAG); live weather query |
| Hybrid memory (F-5) | Conversation > 5 turns → oldest turns summarized; summary + recent 10 messages in prompt | Live: 7 turns → Gemini rolling summary; buffer capped; summary persisted to `conversation_summaries` |
| DB persistence (F-6) | Sessions, messages, summaries survive process restart | Live: SQLite roundtrip in `test_memory.py`; eval runs persisted in `medibot.db` |
| CLI (F-7) | `medibot ingest`, `query`, `evaluate`, `web` all execute without error | Manual runs; pytest via service imports |
| HTTP backend (F-8) | `GET /api/health` returns 200 with status JSON; `/api/sessions` returns sessions; `/docs` shows Swagger | Manual verification |
| Eval framework (F-9) | `runner --category retrieval --limit 2` produces report + DB row with scores | Run id 1: score 7.5; run id 3: score 6.1; eval runs persisted |
| Medical UI (F-10) | Professional landing page + chat UI meeting `medibot-ui-design` skill criteria | 🔜 Phase 6 |
| Source-numbered citations (F-11) | Answer contains `[1]`/`[2]` referencing numbered retrieved docs | ⚠️ Gap — context not numbered; see `07-learning/known-gaps.md` |