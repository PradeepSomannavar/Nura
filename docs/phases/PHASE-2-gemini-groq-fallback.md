# Phase 2 — Gemini Primary + Groq Fallback (Multi-Provider LLM)

**Status:** Completed
**Dependencies:** Phase 1 (service layer)
**Skills to load:** `medibot-architecture`

## Objective

Make **Gemini the primary LLM provider** and keep the current **Groq as the automatic fallback**. Every LLM call (chat streaming, intent classification, memory summarization, evaluation judging) uses a provider router: try Gemini → on failure → Groq → final error. Log which provider served each call for analytics/cost tracking.

## In-Depth Todos

### 1. Add Gemini dependency & config
- [ ] Add `google-generativeai` (or `google-genai`) to `pyproject.toml`.
- [ ] Add `GEMINI_API_KEY`, `GEMINI_MODEL_NAME` (default `gemini-2.5-flash`) to `Settings`.
- [ ] Document Gemini model cheap enough for high quotas.

### 2. `services/llm.py` — provider router
- [ ] Define a unified interface for streaming and non-streaming completion.
- [ ] Implement:
  - `_gemini_stream(prompt, system_instruction)` → yields text chunks using `generate_content(stream=True)`.
  - `_groq_stream(prompt, system_instruction)` → yield chunks via `ChatGroq` or direct HTTP (reuse existing `get_groq_completions_stream` from CinephileGPT pattern).
  - `_gemini_json(prompt)` and `_groq_json(prompt)` for structured JSON completions (intent, memory, evaluation).
- [ ] Implement `stream_completion(prompt, ...)` and `json_completion(prompt, ...)` that try Gemini then Groq.
- [ ] Each router updates an `llm_info["provider"]` dict so callers can log the provider.

### 3. Stream prefix cleaning
- [ ] Add `clean_stream_prefixes(stream)` to strip common model prefixes (`assistant:`, `MediBot:`, `CinephileGPT:`-style, etc.) at stream start (pattern from CinephileGPT `llm.py`).

### 4. Wire provider router into all LLM consumers
- [ ] Chat streaming: `get_chat_stream(...)` uses router.
- [ ] Refusal generator: uses router.
- [ ] Intent classifier: uses router `json_completion`.
- [ ] Memory summarizer (phase 5): uses router.
- [ ] Evaluation judge (phase 6): uses router.
- [ ] Replace any hardcoded single-provider calls.

### 5. Safety settings (Gemini)
- [ ] Set Gemini `safety_settings` appropriately for a medical tool (default/block on harmful categories). Unlike the movie app (BLOCK_NONE), a medical tool should keep sensible blocking — decide and document.

### 6. Error handling & fallback semantics
- [ ] On Gemini exception → log warning → try Groq → log provider.
- [ ] On both failing → yield a professional error message (not raw exception).
- [ ] Never crash the stream on provider outage.
- [ ] Log provider + latency to the metrics store (phase later / reuse analytics stub).

### 7. Tests
- [ ] Unit-test provider selection with mocked Gemini/Groq.
- [ ] Test clean_stream_prefixes with sample model prefixes.
- [ ] Test fallback triggers when primary raises.

### 8. Verification
- [ ] `uv run ruff check`
- [ ] `uv run pytest`
- [ ] Run a chat stream, confirm Gemini used and provider logged.
- [ ] Temporarily break Gemini key → confirm Groq fallback works.

## Definition of Done

- Gemini is primary, Groq is fallback across all LLM calls.
- Provider router handles streaming + JSON with clean fallback.
- Provider + latency logged for analytics.
- Stream prefix cleaning active.
- All tests pass, ruff clean.
