# Non-Functional Requirements

| ID | Requirement | Mechanism / Status |
|----|-------------|--------------------|
| N-1 | **Reliability** — no hard crash on provider outage | Gemini→Groq fallback; on both failing a professional error event, never raw exception ✅ |
| N-2 | **Latency / token budget** — bounded prompt size | Hybrid memory: 10 raw messages (5 turns) + compact rolling summary ✅ |
| N-3 | **Safety** — no diagnosis/prescription; always disclaimer; refuse harmful/off-domain | Intent guard + `MEDICAL_SYSTEM_PROMPT` guardrails + safety eval (2/3 pass) ✅ |
| N-4 | **Security** — never commit/log secrets; API keys only in `.env` (gitignored) | ✅ |
| N-5 | **Maintainability** — layered modules, type hints, docstrings, lint-clean | Python 3.12, ruff (E,F,I,N,W,UP), 56 tests ✅ |
| N-6 | **Testability** — deterministic CI | Unit tests use mock LLM/judge/chain; live checks optional ✅ |
| N-7 | **Observability** — know which provider served + failures | `llm.provider` reported in SSE `sources`/`meta` events; warnings logged ✅ |
| N-8 | **Cost** — cheap primary model | Gemini `gemini-3.6-flash` primary; fallback `openai/gpt-oss-20b` ✅ |
| N-9 | **Scale target** — single-tenant local MVP, SQLite/FAISS | Deferred decisions (Redis cache, Postgres) as ADRs when adopted |

## Acceptance baseline
- Medical queries → grounded answer + disclaimer; non-medical → refusal.
- Memory survives page refresh (DB-backed). [UI wiring pending Phase 6]
- Eval dashboard + SQLite run history accessible.