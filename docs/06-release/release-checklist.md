# Release Checklist

Pre-flight before any release/tag. **Phase 6 blocks the first user-facing release.**

## Quality gates
- [ ] `uv run ruff check src/ tests/` — clean (incl. `app.py` after Phase 6)
- [ ] `uv run ruff format --check src/ tests/` — clean
- [ ] `uv run pytest tests/ -q` — all pass (baseline 56)
- [ ] Live eval benchmark recorded in `05-evaluation/results/` (accuracy + safety ≥ 2/3, citation fixed)
- [ ] Eval dashboard launches + reflects latest run

## Security
- [ ] No secrets committed; `.env` gitignored (`gsk_`, `AQ.` keys absent from repo/`reports/`)
- [ ] No API key/token in logs or telemetry
- [ ] `.env.example` (if present) has placeholder values only

## Behavior
- [ ] Medical query → grounded answer + disclaimer
- [ ] Non-medical / harmful → refusal without RAG (intent guard)
- [ ] >5-turn conversation → summary generated + persisted; refresh restores conversation (Phase 6 wiring)
- [ ] Gemini outage → answer via Groq fallback (no crash)

## Artifacts
- [ ] Phase docs statuses accurate (`docs/phases/`)
- [ ] ADRs updated for any new decisions
- [ ] `06-release/changelog.md` updated
- [ ] Known gaps (`07-learning/known-gaps.md`) reviewed

## Docs
- [ ] `00-overview.md` state table current
- [ ] Test/eval results recorded for this release date