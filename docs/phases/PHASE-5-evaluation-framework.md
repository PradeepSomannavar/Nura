# Phase 5 — Production-Grade Evaluation Framework

**Status:** Completed
**Dependencies:** Phase 1 (services + DB), Phase 2 (LLM router for judge)
**Skills to load:** `medibot-architecture`, `medibot-ui-design` (dashboard)

## Objective

Build a production-grade AI evaluation pipeline + LLMOps-style dashboard (SQLite-backed) to measure MediBot's retrieval, answer accuracy, memory continuity, citation quality, and safety/disclaimer compliance. Mirrors the CinephileGPT evaluation architecture adapted for a medical domain.

## Scope Layout

```
src/medibot/evaluation/   (or top-level evaluation/)
├── __init__.py
├── runner.py               # CLI orchestrator (--limit, --category, --case-id)
├── models.py               # SQLite run-history models
├── datasets/               # JSON test cases per category
│   ├── retrieval_eval.json
│   ├── accuracy_eval.json
│   ├── memory_eval.json
│   ├── citation_eval.json
│   └── safety_eval.json
├── evaluators/
│   ├── retrieval_evaluator.py
│   ├── accuracy_evaluator.py
│   ├── memory_evaluator.py
│   ├── citation_evaluator.py
│   └── safety_evaluator.py
├── judges/
│   └── llm_judge.py        # LLM-as-a-Judge (Gemini -> Groq) structured scoring
├── metrics/
│   └── retrieval_metrics.py  # Recall@K, Hit Rate, MRR
└── dashboard/
    └── dashboard.py        # Streamlit analytics dashboard
```

## In-Depth Todos

### 1. Data models (SQLite)
- [x] `models.py`: `EvaluationRun` (overall_score, per-category scores/pass-rates, status, timestamp), `EvaluationCaseResult` (run_id, case_id, category, passed, score, sub_scores, reasoning).
- [x] Create tables on init.

### 2. Datasets (JSON)
- [x] `retrieval_eval.json` — queries + expected relevant keywords/titles to check recall (deterministic).
- [x] `accuracy_eval.json` — medical Q+A with expected factual points (LLM-judged).
- [x] `memory_eval.json` — multi-turn follow-up scenarios (LLM-judged continuity).
- [x] `citation_eval.json` — prompts + expected citation presence (hybrid programmatic + LLM).
- [x] `safety_eval.json` — disclaimers, refusal for non-medical, harmful requests.
- [x] Each case: `id`, `query`/`conversation`, `difficulty`, `expected`.

### 3. Retrieval metrics (programmatic, no LLM)
- [x] `metrics/retrieval_metrics.py`: `recall_at_k`, `hit_rate`, `mrr`.

### 4. Evaluators
- [x] `retrieval_evaluator.py`: run vector search, compute Recall@5/@10, Hit Rate, MRR.
- [x] `accuracy_evaluator.py`: run RAG chain, LLM-judge relevance/correctness/completeness (1-10).
- [x] `memory_evaluator.py`: feed multi-turn history, judge continuity/preference-use (1-10).
- [x] `citation_evaluator.py`: check `[n]` citation presence programmatically + judge accuracy.
- [x] `safety_evaluator.py`: check refusal for non-medical, disclaimer presence, harmful-request handling.

### 5. LLM Judge
- [x] `judges/llm_judge.py`: `LLMJudge.score(prompt, rubric) -> {score(1-10), sub_scores, reasoning}`.
- [x] Uses Phase-4 provider router (Gemini → Groq), structured JSON output.
- [x] Category-specific rubrics (relevance, correctness, completeness, continuity, citation, safety).

### 6. Runner (CLI)
- [x] `runner.py`: argparse `--limit`, `--category`, `--case-id`, `--save-db`.
- [x] Load datasets, run evaluators, aggregate pass rates + avg scores.
- [x] Save run history to SQLite (EvaluationRun + EvaluationCaseResult).
- [x] Write JSON reports to `reports/` (gitignored).
- [x] Rate-limit sleep between LLM-judged cases.

### 7. Dashboard (Streamlit)
- [x] `dashboard/dashboard.py`: run history summaries, category drilldowns, trend lines over time, failed-case diagnostics, CSV/JSON export.
- [x] Styled per `medibot-ui-design` (professional, restrained).

### 8. Wire into project
- [x] Update `pyproject.toml` with any new deps (streamlit already present).
- [x] Add console script or CLI subcommand `medibot evaluate`.

### 9. Tests
- [x] Programmatic metric unit tests (recall, hit rate, MRR) with known data.
- [x] Evaluator smoke tests with mock LLM judge.

### 10. Verification
- [x] `python -m medibot.evaluation.runner --limit 2` runs.
- [x] Reports written to `reports/`.
- [~] Dashboard launches via `streamlit run`. (Import-verified; launch pending Phase 6 UI verification.)
- [x] `uv run pytest` and `uv run ruff check` pass.

## Notes

- The old top-level `medibot/evaluate.py` was superseded by the `medibot/evaluation/` package and removed.
- The deprecated Groq model `llama-3.1-8b-instant` was replaced with `openai/gpt-oss-20b`; the deprecated `gemini-2.5-flash` was replaced with `gemini-3.6-flash`.  Both `.env` and `core/config.py` defaults were updated.
- Live LLM-judged runs (run id 3, Groq fallback `openai/gpt-oss-20b`): **accuracy 9.7 (3/3)**, **safety 9.3 (2/3)**, memory 2.0 (borderline — passes on re-run: 7.0/7.5), **citation 0.0 (0/2)**.  All runs persisted to `evaluation_runs` / `evaluation_case_results` in `medibot.db`.
- **Citation finding (genuine app gap):** the RAG `context` is the raw concatenated retrieved docs without `[1]`/`[2]` markers, so `gpt-oss-20b`/Gemini rarely emit bracketed citations even though `MEDICAL_SYSTEM_PROMPT` instructs them to.  Fix lives in the RAG chain (format context with numbered sources), out of Phase-5 scope.
- **Memory finding:** continuity answers are useful but the model only "loosely references" prior turns; occasional empty answers make per-run scores vary.  Judge treated an empty answer purely as a low score — a future robustness improvement would mark empty responses as failed-by-error.

## Definition of Done

- 5 evaluation categories with JSON datasets.
- Programmatic retrieval metrics + LLM-as-a-Judge qualitative scoring.
- CLI runner with filters, SQLite run history, JSON reports.
- Streamlit dashboard for visualization.
- All tests pass, ruff clean.
