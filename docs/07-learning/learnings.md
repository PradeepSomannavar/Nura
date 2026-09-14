# Learnings & Strategies

Lessons captured to improve how we build phases next time. Short, actionable.

## Process / workflow
1. **Load the skills + phase doc BEFORE coding** — `medibot-architecture`, `medibot-ui-design`; each phase doc drives the todo list.
2. **Verify as you go** — after each reusable service, run ruff + pytest; fixing 1 file is cheaper than 10.
3. **Live-verify only after unit tests** — deterministic CI (mock LLM/judge), then a live smoke for reality checks.
4. **Record eval runs like data** — always persist to DB + JSON and link run ids in `05-evaluation/results/`; you can't improve what you can't compare.
5. **Pin and track model versions** — provider model names retire (this project lost `llama-3.1-8b-instant` and `gemini-2.5-flash` mid-roadmap). Keep models in `Settings`; re-check availability when keys/accounts change.

## Architecture / code
6. **Prompts live in `prompts/`** — never inline; makes prompt tuning and eval review isolated from service logic.
7. **Config only via `Settings`** — scattered `os.getenv` is how secrets and defaults drift.
8. **One provider router for every LLM call** — intent / memory / judge all reuse `FallbackChatModel`; fallback is free once implemented once.
9. **Be explicit about chain input contracts** — the real RAG chain requires `chat_history` (even empty); stub chains can miss this and pass tests while live fails.
10. **Graceful degradation everywhere** — refusal string when LLM classifier down; neutral 0.0 judge on parse failure; provider fallback.

## RAG / eval lessons
11. **An eval finding that's consistent across models is an app gap, not a flake** — citation 0/2 across runs pointed at unnumbered context; fixing the product beats re-tuning the rubric.
12. **Judge variance is real** — LLM judges wobble near the pass line (memory 0/2 vs 7.0/7.5). Plan for majority voting or tighten rubrics for stable thresholds.
13. **Watch the models, not just the metrics** — Gemini 429 made live runs 5× slower (62s retry storm before fallback); consider fail-fast on auth errors.

## Things to try next
- Fail-fast fallback on 401/429 (avoid 62s retry wait).
- Number context sources → close G1 and re-benchmark.
- Majority-of-3 judge for memory/citation stability.
- Phase 6 UI: apply `medibot-ui-design` + `design-taste-frontend`, then wire `HybridMemory` restore (G3).