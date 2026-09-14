# Data Flow

## 1. Chat (UI / CLI / API → answer)

```
user message
   │  (POST /api/chat/stream  OR  services.chat.answer_stream)
   ▼
[1] IntentService.classify   → meta event carries intent
   ├─ NON_MEDICAL / HARMFUL_REQUEST
   │     ▼  refusal_stream (no RAG, no retrieval)  → token + done
   └─ MEDICAL_QUERY
         ▼
[2] HybridMemory(session_id).add_message(user)     → persist to chat_messages
         ▼
[3] build_context()  = [summary SystemMessage] + [last 5 raw turns]
         ▼
[4] RAG chain (build_rag_chain)
   ├─ history-aware retriever (reformulates query w/ chat_history)
   ├─ FAISS similarity_search → top-k docs
   └─ LLM (Gemini→Groq) w/ QA_PROMPT (context + chat_history + input)
         ▼
[5] stream token chunks → sources event (provider) → assistant msg persisted → evict_and_summarize if > buffer
   ▼
done event
```

SSE events: `meta` (intent) · `token` (content chunk) · `sources` (docs + provider) · `done` / `error`.

## 2. Memory (eviction & summarization)

```
buffer > buffer_turns × 2  →  evict oldest 2 turns
   → summarize_conversation(existing_summary, evicted)
   → merge into rolling summary
   → persist ConversationSummary (ON CONFLICT update)
   → keep only recent buffer in prompt
```

## 3. Evaluation pipeline

```
runner --category <cat> [--limit N] [--case-id X]
   ▼ load_cases(datasets/<cat>.json)
   ▼ build_evaluator (retrieval: similarity_search; others: RAG chain + LLMJudge)
   ▼ evaluate(case) → CaseOutcome{passed, score, sub_scores, reasoning}
   ▼ aggregate → report {overall, per-category}
   ▼ save EvaluationRun + EvaluationCaseResult → medibot.db
   ▼ optional JSON report → reports/evaluation-<ts>.json  (gitignored)
   ▼ Streamlit dashboard reads medibot.db for KPIs/trend/failures
```

## 4. LLM router (all calls)

```
get_llm().invoke/stream
   ▼ FallbackChatModel._generate/_stream
   ├─ Gemini → success → return (provider=gemini)
   └─ raise  → log warning → Groq → success → return (provider=groq)
              └─ raise → RuntimeError("All LLM providers failed")
```