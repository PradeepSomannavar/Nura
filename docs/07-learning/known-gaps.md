# Known Gaps & Pending Work

Single registry of unfinished/deferred items. Each has owner-phase and unblocks.

## [G1] Source-numbered citations in answers (F-11) — HIGH
- **Symptom:** Citation eval 0/2; answers never contain `[n]`.
- **Cause:** RAG `context` = raw concatenated docs, no `[1]/[2]` markers, so the `[n]` instruction in `MEDICAL_SYSTEM_PROMPT` cannot be satisfied.
- **Fix:** `services/rag.py` — number retrieved docs when formatting context (e.g. `[1] <doc>`), confirm `[n]` via citation eval. → then re-benchmark.

## [G2] Streamlit UI redesign (Phase 6) + `app.py` ruff cleanup
- `app.py` carries pre-existing ruff violations (CSS/text blocks, import sort, f-strings). Redesign is the explicit next phase; load `medibot-ui-design` + `design-taste-frontend`.

## [G3] Frontend memory restore wiring (Phase 4 §6)
- Service-level memory is DB-backed and verified; Streamlit UI still feeds raw `st.session_state` messages into chat (doesn't use `HybridMemory` yet). Canvas for Phase 6.

## [G4] Stub services
- `services/cache.py` (NoOp) and `services/analytics.py` (basic) — Redis cache + metrics/analytics adopted in a future phase.

## [G5] Eval tooling hardenings
- LLM judge treats an empty answer as a low score — improvement: mark as failed-by-error with distinct reasoning.
- Judge variance on LLM-based scoring (memory 0/2 → pass on re-run) — consider majority-of-3 or rubric tightening.
- `MEMORY_SUMMARY_STORE` default `"sqlite"` — file-JSON fallback path unused/untested.

## [G6] Operations / credentials
- Gemini API key currently 429 (quota) — live runs fall back to Groq; re-verify Gemini path when quota restored.
- `dashboard.py` import-verified; full `streamlit run` launch smoke deferred to Phase 6.
- `reports/` is gitignored — periodic archiving of eval reports is manual.

## Deferred items (conscious choices)
- Redis cache, Postgres, multi-user auth, real analytics → not in current MVP.
- OCR / multilingual ingest → not required yet.