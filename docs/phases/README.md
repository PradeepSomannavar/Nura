# MediBot Production Roadmap

Step-by-step phased upgrade of MediBot toward a production-grade, modular RAG application. Each phase has its own in-depth planning doc with actionable todos.

> **Docs home →** [`docs/00-overview.md`](../00-overview.md) for the full project docs (requirements / design / implementation / testing / evaluation / release / learning).
> **Architecture →** [`ARCHITECTURE.md`](../../ARCHITECTURE.md) for the full architecture diagram, current file structure, and key modules.
> **Status →** [`docs/03-implementation/tasks.md`](../03-implementation/tasks.md); evidence in [`docs/04-testing/`](../04-testing/) and [`docs/05-evaluation/`](../05-evaluation/).

## Phase Order (UI redesign is LAST)

Execution order is intentional: correctness, structure, and behavior first; cosmetics last. Each phase builds on the previous.

| # | Doc | Focus | Depends on |
|---|-----|-------|-----------|
| 1 | [PHASE-1-fastapi-backend.md](PHASE-1-fastapi-backend.md) | Modular service-oriented FastAPI backend | — |
| 2 | [PHASE-2-gemini-groq-fallback.md](PHASE-2-gemini-groq-fallback.md) | Gemini primary + Groq fallback (multi-provider) | Phase 1 |
| 3 | [PHASE-3-intent-guardrails.md](PHASE-3-intent-guardrails.md) | Intent classifier + domain guardrails (medical-only) | Phase 1, 2 |
| 4 | [PHASE-4-hybrid-memory.md](PHASE-4-hybrid-memory.md) | Hybrid memory (5-turn buffer + rolling summary, SQLite) | Phase 1, 2 |
| 5 | [PHASE-5-evaluation-framework.md](PHASE-5-evaluation-framework.md) | Production evaluation framework + dashboard | Phase 1, 2, 3, 4 |
| 6 | [PHASE-6-ui-redesign.md](PHASE-6-ui-redesign.md) | Professional, medical-grade UI redesign | All prior |

## Why UI Redesign is Last

1. The backend refactor (Phase 1) changes how the UI consumes data (SSE streaming, memory, guardrails). Designing UI against a moving backend is wasted work.
2. New features (memory, citations via guardrails, provider selection) surface **new UI states** — a redesign done after these exist is complete; one done before must be redone.
3. Correctness and security matter more than cosmetics for a medical tool. The UI polish is the final layer.

## Reference Materials

- **Main architecture doc:** [`ARCHITECTURE.md`](../../ARCHITECTURE.md)
- **UI design guidelines:** `medibot-ui-design` + `design-taste-frontend` + `web-design-guidelines` skills (`.opencode/skills/`)
- **Architecture guidelines:** `medibot-architecture` skill (`.opencode/skills/`)
- **Inspiration:** CinephileGPT architecture (FastAPI, hybrid RAG, multi-tiered memory, Redis caching, structured logging/analytics, evaluation framework)

## Summary of Target Architecture (after all phases)

See [`ARCHITECTURE.md`](../../ARCHITECTURE.md) for the target-state diagram and the full layered file structure.

```
┌───────────────────────────────────────────────┐
│              PRESENTATION LAYER                 │
│  Streamlit / SPA  ↔  FastAPI (SSE streaming)   │
└───────────────────┬───────────────────────────┘
                    │
┌───────────────────▼───────────────────────────┐
│               APPLICATION (api/)               │
│  chat.py  memory.py  analytics.py  health.py   │
└───────────────────┬───────────────────────────┘
                    │
┌───────────────────▼───────────────────────────┐
│                   CORE                         │
│  config (Settings)  database  security  logging│
└───────────────────┬───────────────────────────┘
                    │
┌───────────────────▼───────────────────────────┐
│                   SERVICES                     │
│  llm (Gemini→Groq)  retrieval  embeddings      │
│  intent/guardrails  memory  cache  analytics    │
│        │            │            │             │
│   ┌────▼────┐  ┌────▼────┐   ┌────▼────┐      │
│   │ FAISS   │  │ SQLite  │   │ Redis   │      │
│   │ index   │  │ (memory/│   │ (cache)  │      │
│   │         │  │  logs)  │   │          │      │
│   └─────────┘  └─────────┘   └─────────┘      │
└───────────────────────────────────────────────┘

Evaluation: runner + LLM-as-a-Judge + SQLite history + dashboard
```

## How to Run a Phase

1. Load the phase doc + relevant skill (see `AGENTS.md`).
2. Read `ARCHITECTURE.md` to understand how the phase fits the whole.
3. Implement todos in order.
4. Verify: `uv run ruff check src/ tests/` and `uv run pytest tests/ -v`.
5. Commit only when explicitly requested.
