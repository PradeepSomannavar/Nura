# Phase 4 — Hybrid Memory System (Buffer + Summary)

**Status:** Completed
**Dependencies:** Phase 1 (services + DB), Phase 2 (LLM router for summarizer)
**Skills to load:** `medibot-architecture`

## Objective

Implement a **hybrid conversation memory**: keep the last **5 turns (10 messages)** as a raw buffer in the prompt (conversation buffer memory), and compress **older evicted turns into a rolling summary** persisted to SQLite (long-term summary memory). This bounds token cost while preserving clinical continuity across a long session and across page refreshes.

## In-Depth Todos

### 1. Config
- [x] Add `MEMORY_BUFFER_TURNS` (default `5`) → buffer_max = turns × 2 messages.
- [x] Add optional `MEMORY_SUMMARY_STORE` (`sqlite`) path setting.

### 2. `services/memory.py` — HybridMemory service
- [x] Class `HybridMemory(session_id, db=None, buffer_turns=...)`.
- [x] Manage an ordered raw buffer of `{role, content, ts}` for the current session (in-memory while running).
- [x] **Eviction & summarization:** when raw buffer exceeds `buffer_max`, evict the oldest 2 turns (4 messages), LLM-summarize them (merged with existing summary), persist summary to DB.
- [x] Persist chat messages to DB (`ChatMessage`) for durability.
- [x] `build_chat_history()` returns a list for the RAG prompt:
  1. Optional `SystemMessage` summarizing prior context: `"[Previous conversation summary] ..."` (if summary exists).
  2. The raw buffer messages as `HumanMessage`/`AIMessage`.

### 3. Summarizer
- [x] `services/llm.py` or `services/summarizer.py`: `summarize_conversation(existing_summary, new_messages) -> str`.
- [x] Returns a concise **clinical** summary (2–4 sentences): conditions discussed, symptoms, treatments advised, open follow-ups.
- [x] Uses the Phase-4 provider router (Gemini → Groq).
- [x] Merge rules: combine new summary with existing; avoid duplication; keep it compact.

### 4. Persistence (SQLite)
- [x] Model `ConversationSummary`: `session_id`, `summary_text`, `updated_at`.
- [x] Model `ChatMessage`: already from Phase 2.
- [x] Load summary on session start; save on eviction and/or session end.

### 5. Wire into RAG chain consumers
- [x] Update `api/chat.py` streaming route to use `HybridMemory.build_chat_history()` instead of the current all-messages loop (`app.py` currently passes every message).
- [x] Ensure the LLM sees summary + recent buffer.
- [x] `CONTEXTUALIZE_Q_PROMPT` and `QA_PROMPT` already use `MessagesPlaceholder("chat_history")` — passing the constructed list works without prompt changes.

### 6. Frontend (Streamlit / SPA) integration
- [ ] Update `app.py` to feed messages through `HybridMemory` service rather than raw `st.session_state.messages`.
- [ ] On page refresh, reload message buffer + summary from DB by session id.

### 7. Tests
- [x] Unit-test eviction: after > buffer_max messages, oldest turns moved to summary.
- [x] Test `build_chat_history` shape (summary SystemMessage + recent buffer).
- [x] Test summary persistence round-trip in SQLite.
- [x] Mock LLM summarizer for deterministic tests.

### 8. Verification
- [x] `uv run ruff check`
- [x] `uv run pytest`
- [x] Start a long conversation (>5 turns), confirm the older turns are summarized and summary appears in subsequent prompts.
- [~] Refresh page → conversation state restored from DB (buffer + summary). (Service-level verified; Streamlit UI wiring is part of Phase 6.)

## Definition of Done

- Last 5 turns (10 messages) in prompt as raw buffer.
- Older turns compressed into a rolling, persisted summary (SQLite).
- Summary + buffer both injected in correct format.
- Memory survives page refresh (DB-backed).
- Token cost bounded (only 10 raw messages + summary in prompt).
- Tests pass, ruff clean.
