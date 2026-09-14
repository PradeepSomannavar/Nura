# Test Cases

Suite: **56 tests passing** (2026-09-13). Run in ~12s.

| File | Tests | Covers |
|------|-------|--------|
| `tests/test_config.py` | Settings | env/default loading, model defaults |
| `tests/test_api.py` | API/routers | health + chat stream smoke |
| `tests/test_vectorstore.py` | FAISS | vectorstore build/load |
| `tests/test_ingestion.py` | Ingestion | PDF load + chunking |
| `tests/test_llm.py` | LLM router | fallback trigger, prefix cleanup |
| `tests/test_intent.py` | 14 | intent classification, keyword fallback, non-medical does not run retrieval |
| `tests/test_memory.py` | 5 | eviction at threshold, buffer cap, summary prefix, SQLite round-trip |
| `tests/test_evaluation.py` | 9 | evaluator wiring (stubs), runner reports + DB persistence |
| `tests/test_evaluation_metrics.py` | 10 | recall@k, hit rate, MRR (known data) |

## Test doubles (pattern)
- `_FakeChain` → returns canned `{"answer": ...}`; accepts `chat_history`.
- `_FakeJudge` → returns fixed `JudgeResult`.
- `_FakeSearch` → returns fixed document list.
- `_FakeIntent` / monkeypatched `SessionLocal` + `init_db` → in-memory SQLite.
- LLM summarizer mocked for deterministic memory tests.

## Regression notes
- Evaluator chain invocations **must pass `chat_history`** (real RAG chain requires the key, even empty) — `accuracy`/`citation`/`safety-evaluator` fixed for this.
- Runner uses `PROJECT_ROOT` from `core/config.py` (module-level constant), not a `Settings` attribute.