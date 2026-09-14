# Interfaces

## HTTP API (FastAPI)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/chat/stream` | SSE chat: events `meta`(intent) · `token` · `sources` · `done` · `error` |
| GET | `/api/health` | Status + vectorstore-ready flag |
| POST | `/api/sessions` | Create a session |
| GET | `/api/sessions/{session_id}/messages` | Load message history |
| GET | `/api/analytics` | Metrics (basic) |

`ChatStreamEvent` schema: `type`, `content`, `provider`, `sources[]` (`SourceDoc{content, metadata}`).
Swagger: http://localhost:8000/docs.

## CLI
```
medibot ingest      Build FAISS index from PDFs in data/
medibot query       Interactive CLI query
medibot evaluate    Run evaluation suite (see --help: --category/--limit/--case-id/--report-dir/--no-save-db/--sleep)
medibot web         Launch Streamlit web interface
```

## Service surfaces (imports used across layers)
| Module | Key exports |
|--------|-------------|
| `services.llm` | `get_llm()`, `get_active_provider()`, `clean_stream_prefixes` |
| `services.chat` | `answer_stream(message, history, session_id)`, `ChatStreamEvent`-style yields |
| `services.intent` | `IntentService`, `classify_intent`, `refusal_stream` |
| `services.memory` | `HybridMemory(session_id, db, buffer_turns)` |
| `services.rag` | `build_rag_chain(vectorstore, k)` |
| `services.retrieval` | `load_vectorstore`, `similarity_search`, `build_and_save_vectorstore` |
| `services.summarizer` | `summarize_conversation`, `format_summary_messages` |
| `core.config` | `Settings` singleton + `PROJECT_ROOT` |

## Prompts (single source of truth)
`prompts/qa.py` (MEDICAL_SYSTEM_PROMPT, QA_PROMPT) · `contextualize.py` · `intent.py` (classifier + refusal) · `memory.py` (summary system) · `judge.py` (rubrics + JSON schema). **Never inline prompts in services/routes/UI.**

## Eval runner CLI
`python -m medibot.evaluation.runner --category retrieval|accuracy|memory|citation|safety [--limit N] [--case-id ID] [--sleep S] [--no-save-db]`
Output: console summary + `EvaluationRun`/`EvaluationCaseResult` rows + optional JSON report in `reports/`.

## DB tables (SQLite)
`chat_sessions`, `chat_messages`, `conversation_summaries`, `evaluation_runs`, `evaluation_case_results`.