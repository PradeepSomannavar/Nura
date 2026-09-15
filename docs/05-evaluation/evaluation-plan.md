# Evaluation Plan

Purpose: quantify MediBot quality per category, catch regressions, and drive fixes. Mirrors an LLMOps loop: datasets → evaluators → judge → run history → dashboard → fix.

## Categories & evaluators
| Category | Evaluator | Method | Dataset |
|----------|-----------|--------|---------|
| retrieval | `RetrievalEvaluator` | Programmatic keyword recall in top-k (no LLM) | retrieval_eval.json (5) |
| accuracy | `AccuracyEvaluator` | RAG chain answer → LLM judge | accuracy_eval.json (3) |
| memory | `MemoryEvaluator` | Multi-turn chain w/ history → continuity judge | memory_eval.json (2) |
| citation | `CitationEvaluator` | Regex `[n]` check + judge | citation_eval.json (2) |
| safety | `SafetyEvaluator` | Strict refusal of non-medical/math/coding/harmful + judge | safety_eval.json (4) |

## Runner
`python -m medibot.evaluation.runner [--category X] [--limit N] [--case-id ID] [--sleep S] [--report-dir DIR] [--no-save-db]`

- Cases → outcomes → aggregate → persist `EvaluationRun` + `EvaluationCaseResult` → optional JSON report (`reports/`, gitignored).
- Rate-limit sleep between LLM-judged cases.

## Judge
`LLMJudge.score(category, question, answer, expected, context)` → `JudgeResult{score, sub_scores, reasoning}`.
Rubrics in `prompts/judge.py`; category-specific (relevance, correctness, completeness, continuity, citation, safety).
Uses Gemini→Groq router; graceful 0.0 + reasoning on parse failure.

## Dashboard
`uv run streamlit run src/medibot/evaluation/dashboard/dashboard.py`
KPIs, per-category bars, score trend, failed-case diagnostics, CSV/JSON export.

## Running strategy
- CI-deterministic: retrieval + stubbed evaluators (unit tests).
- Weekly/human: full live run (all categories), record in `05-evaluation/results/`.
- On model/domain-changes: re-benchmark to detect drift.