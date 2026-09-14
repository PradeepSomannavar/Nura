# Components

| Component | Path | Responsibility | Status |
|-----------|------|----------------|--------|
| FastAPI app | `main.py` | App factory, CORS, routers, DB init | ✅ |
| Chat router | `api/chat.py` | `POST /api/chat/stream` (SSE) | ✅ |
| Health router | `api/health.py` | `GET /api/health` — status + vectorstore flag | ✅ |
| Memory router | `api/memory.py` | Sessions + message history endpoints | ✅ |
| Analytics router | `api/analytics.py` | Metrics endpoint | ✅ (basic) |
| Config | `core/config.py` | `Settings` singleton, all env config | ✅ |
| Database | `core/database.py` | Engine, `SessionLocal`, `Base`, `init_db` | ✅ |
| Logging | `core/logging.py` | Central logging setup | ✅ |
| ORM models | `models/memory.py`, `models/evaluation.py` | ChatSession/Message/Summary + EvalRun/RunResult | ✅ |
| Schemas | `schemas/chat.py` | `ChatRequest`, `ChatStreamEvent`, `SourceDoc` | ✅ |
| Chat service | `services/chat.py` | `answer_stream`: intent → memory → RAG → events | ✅ |
| Intent | `services/intent.py` | `IntentService`, keyword fallback, refusal stream | ✅ |
| LLM router | `services/llm.py` | `FallbackChatModel` Gemini→Groq, provider tracking | ✅ |
| RAG | `services/rag.py` | `build_rag_chain` (history-aware retriever + stuff) | ✅ |
| Retrieval | `services/retrieval.py` | FAISS load/search, cached per process | ✅ |
| Embeddings | `services/embeddings.py` | `get_embedding_model()` | ✅ |
| Ingestion | `services/ingestion.py` | PDF load, chunking | ✅ |
| Memory | `services/memory.py` | `HybridMemory` buffer+summary, SQLite | ✅ |
| Summarizer | `services/summarizer.py` | `summarize_conversation`, `format_summary_messages` | ✅ |
| Cache | `services/cache.py` | Interface + NoOp impl | ✅ (stub) |
| Analytics | `services/analytics.py` | Stub metrics accumulator | ✅ (stub) |
| Prompts | `prompts/` | qa, contextualize, intent, memory, judge | ✅ |
| Eval runner | `evaluation/runner.py` | CLI orchestrator, DB + JSON reports | ✅ |
| Judge | `evaluation/judges/llm_judge.py` | LLM-as-a-Judge, category rubrics | ✅ |
| Evaluators | `evaluation/evaluators/` | 5 category evaluators | ✅ |
| Metrics | `evaluation/metrics/retrieval_metrics.py` | Recall@K, Hit Rate, MRR | ✅ |
| Datasets | `evaluation/datasets/*.json` | 15 test cases | ✅ |
| Eval dashboard | `evaluation/dashboard/dashboard.py` | Streamlit analytics | ✅ (import-verified) |
| CLI | `cli.py` | `ingest / query / evaluate / web` | ✅ |
| UI | `app.py` | Streamlit landing + chat | 🔜 Phase 6 redesign |