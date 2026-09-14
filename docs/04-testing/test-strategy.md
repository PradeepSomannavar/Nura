# Test Strategy

## Principles
- **Deterministic first**: unit tests mock LLM judge, retrieval chain, and fake-search for CI.
- **Live smoke second**: provider-connected smoke runs optional (memory/accuracy live verifications).
- **Ruff clean**: every run; violations are commit-blockers.

## Coverage scope
| Layer | What tests cover |
|-------|------------------|
| Config | Settings loading, default values, `PROJECT_ROOT` |
| Services | Intent classification (LLM mock + keyword fallback), RAG chain smoke (stubbed chain/judge), retrieval (vectorstore), ingestion |
| Memory | Eviction threshold, buffer capped, summary prefix, SQLite round-trip |
| Evaluation metrics | `recall_at_k`, `hit_rate`, `mrr_at_k` with known data |
| Evaluation evaluators | Stubs: `_FakeSearch`, `_FakeChain`, `_FakeJudge`, `_FakeIntent` — exercises correct wiring |
| Runner | Retrieval run persists report + in-memory SQLite via monkeypatch |

## Commands
```bash
uv run ruff check src/ tests/       # lint
uv run ruff format --check src/     # format check
uv run pytest tests/ -q            # 56 passed (2026-09-13)
uv run pytest tests/test_memory.py -v  # focused
```

## Known gaps in test coverage
- No live LLM-judge unit tests in CI (env-dependent) — live runs done manually and recorded in `04-testing/test-results/`.
- `app.py` ruff violations are excluded from per-phase ruff checks (UI code, Phase 6).
- `test_api.py` coverage is basic (smoke-level).