# Phase 3 — Intent Classifier & Domain Guardrails

**Status:** Completed
**Dependencies:** Phase 1 (backend structure), Phase 2 (LLM router)
**Skills to load:** `medibot-architecture`

## Objective

Add a domain guard so **MediBot only answers medical/health-related queries**. An LLM-based intent classifier routes each user message to `MEDICAL_QUERY` or `NON_MEDICAL`. Non-medical queries get a **polite, in-character refusal** (no off-domain answers). Safety guardrails enforce citations + disclaimer.

## In-Depth Todos

### 1. `services/intent.py` — Intent classifier
- [ ] Define `classify_intent(message: str, history: list = None) -> str` returning one of:
  - `MEDICAL_QUERY` — medical/health/clinical question.
  - `NON_MEDICAL` — anything else (coding, cooking, weather, general chat).
- [ ] Use LLM (Gemini primary, Groq fallback) with `response_mime_type: application/json` → return `{"intent": "..."}`.
- [ ] Include recent history context (last 3 turns) for reference resolution.
- [ ] Deterministic fallback: simple medical keyword heuristic if both LLMs fail (list of medical terms: symptom prefixes, anatomy terms, "symptoms", "treatment", "diagnosis", "drug", "disease", etc.). Default to `MEDICAL_QUERY` on total failure? Decide and document (safer: allow but still enforce disclaimer — decide in kickoff).

### 2. Refusal response generator (guardrail)
- [ ] `services/intent.py` or `services/llm.py`: `get_refusal_stream(message)`.
- [ ] Generates a **brief, professional** refusal: "I'm MediBot, a clinical reference assistant focused only on medical and health questions..." — redirect to medical topics.
- [ ] Keep it concise (1–2 sentences), professional (NOT humorous — medical context). No off-domain info.
- [ ] Provider fallback chain (Gemini → Groq → static text).

### 3. Wire classifier into streaming chat
- [ ] In `api/chat.py` streaming route: classify intent on each message.
- [ ] `NON_MEDICAL` → stream `get_refusal_stream` and stop (do not run RAG).
- [ ] `MEDICAL_QUERY` → run normal RAG pipeline.
- [ ] Send a `meta` SSE event with the classified intent (like CinephileGPT `meta` event).

### 4. Safety guardrails on answers
- [ ] Enforce mandatory medical disclaimer appended to every answer (already in prompt; add a programmatic check/post-processor if needed).
- [ ] Enforce citation requirement: prompt already requests `[1]`,`[2]`; add evaluation check in phase 6.
- [ ] Refuse harmful/irresponsible diagnostic prescriptions: add a guard prompt line — "Never provide definitive diagnosis or prescribe medication; recommend consulting a licensed professional." (Extend `MEDICAL_SYSTEM_PROMPT`.)
- [ ] Do not run retrieval or spend LLM tokens on clearly off-domain queries (route to refusal early).

### 5. Config additions
- [ ] Add settings for guardrail switches: e.g. `ENABLE_INTENT_GUARD` (default true), optional `GUARDRAIL_STRICT` mode.

### 6. Tests
- [ ] Unit-test `classify_intent` with representative medical vs non-medical samples (mock or real LLM — use mock/fixture for CI determinism, optional live check).
- [ ] Test keyword-fallback heuristic directly.
- [ ] Test that `NON_MEDICAL` messages do not invoke retrieval.

### 7. Verification
- [ ] Sending "What's the weather?" → professional refusal, no retrieval.
- [ ] Sending "What are hypertension symptoms?" → normal RAG answer + disclaimer.
- [ ] `uv run ruff check` and `uv run pytest` pass.

## Definition of Done

- Intent classifier routes medical vs non-medical reliably (with LLM + heuristic fallback).
- Non-medical queries produce a brief professional refusal without running RAG.
- Medical answers always carry disclaimer + citations.
- Guardrails active and configurable via settings.
- Tests pass, ruff clean.
