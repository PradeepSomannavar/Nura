# Benchmarks

Full runs persisted in `medibot.db` (`evaluation_runs`). Dashboard shows trend; these notes capture context.

## Run history
| Run | Date | Categories | Score | Pass | Notes |
|-----|------|-----------|-------|------|-------|
| 1 | 2026-09-13 | retrieval ×2 | 7.5 | 2/2 | Live, no LLM, report JSON written |
| 2 | 2026-09-13 | accuracy ×1 | 10.0 | 1/1 | Live via Groq fallback |
| 3 | 2026-09-13 | accuracy 3 · citation 2 · memory 2 · safety 3 | 6.1 | accuracy 3/3, safety 2/3, memory 0/2, citation 0/2 | Full live LLM-judged (Groq); memory re-run later passed 7.0/7.5 |

## How to benchmark
```bash
uv run python -m medibot.evaluation.runner                    # all categories
uv run python -m medibot.evaluation.runner --category accuracy --limit 1
uv run python -m medibot.evaluation.runner --case-id accuracy-hypertension-symptoms
uv run streamlit run src/medibot/evaluation/dashboard/dashboard.py   # view history
```

## Provider reality check (2026-09-13)
- Gemini key hits 429 quota (plan/billing) → live runs fall back to Groq (`openai/gpt-oss-20b`).
- Model churn: `llama-3.1-8b-instant` and `gemini-2.5-flash` retired; replaced as `ADR-002`.
- When Gemini works, expect provider `gemini`; scores may shift model-to-model.