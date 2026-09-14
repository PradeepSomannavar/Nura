# MediBot — Project Overview

RAG-based clinical reference assistant. Production roadmap applied in phases:
correctness → structure → behavior → evaluation → cosmetics (UI last).

## Current State (2026-09-13)

| Dimension | Status |
|-----------|--------|
| Phases 1–5 | ✅ Completed (modular backend, multi-provider LLM, intent guard, hybrid memory, eval framework) |
| Phase 6 (UI redesign) | 🔜 Next |
| Test suite | 56 passing, ruff clean |
| Eval benchmark | Accuracy 3/3 · Safety 2/3 · Memory borderline · Citation 0/2 (finding → fix in RAG chain) |

## Docs Map

| Section | Covers |
|---------|--------|
| [01-requirements](01-requirements/functional.md) | What the system must do (functional / non-functional / acceptance) |
| [02-design](02-design/architecture.md) | Architecture, components, data flow, ADRs |
| [03-implementation](03-implementation/tasks.md) | Phase status, tasks, interfaces |
| [04-testing](04-testing/test-strategy.md) | Test strategy, cases, recorded results |
| [05-evaluation](05-evaluation/evaluation-plan.md) | Eval plan, metrics, benchmarks, results |
| [06-release](06-release/release-checklist.md) | Release checklist, changelog |
| [07-learning](07-learning/known-gaps.md) | Known gaps/pending, learnings/strategies |

## Planning Docs (unchanged, referenced)
- Roadmap: [`phases/README.md`](phases/README.md) · phase plans: [`phases/`](phases/)
- Full target architecture: [`ARCHITECTURE.md`](../ARCHITECTURE.md)

## Canonical Commands
- Tests: `uv run pytest tests/ -q` (56 passed)
- Lint: `uv run ruff check src/ tests/`
- App: `uv run medibot web` (http://localhost:8501)
- API: `uv run uvicorn medibot.main:app --reload` (http://localhost:8000/docs)
- Eval: `uv run python -m medibot.evaluation.runner --category <cat> [--limit N]`
- Eval dashboard: `uv run streamlit run src/medibot/evaluation/dashboard/dashboard.py`