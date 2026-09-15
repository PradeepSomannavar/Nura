# Evaluation Metrics

## Programmatic retrieval metrics (`evaluation/metrics/retrieval_metrics.py`)
| Metric | Definition | Max |
|--------|-----------|-----|
| `recall_at_k` | fraction of expected keywords found among top-k retrieved docs | 1.0 |
| `hit_rate` | whether any relevant doc is in top-k | 1.0 |
| `mrr_at_k` | 1 / rank of first relevant doc (0 if none in top-k) | 1.0 |
| `mean_reciprocal_rank` | mean MRR across queries | 1.0 |

Deterministic, no LLM.

## LLM-judge scoring
1–10 scale per category with sub-scores aligned to rubric:

| Rubric axis | Applies to |
|-------------|------------|
| Relevance | accuracy |
| Correctness | accuracy, citation |
| Completeness | accuracy |
| Continuity / context-use | memory |
| Citation presence + accuracy | citation |
| Safety (strict refusal, scope) | safety |

Pass threshold: `score >= 7.0` (see `LLMJudgeScore.passed()`).

## Run-level aggregates
- Per-category: `score` (mean), `passed/total`, `pass_rate`.
- Overall run score = mean of category scores.

## Limitations
- Judge is LLM-based → non-deterministic; small variance seen on memory cases (0/2 → 7.0/7.5 on re-run).
- Empty answers currently score low rather than flagging failed-by-error (future improvement).