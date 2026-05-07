"""Evaluation suite for MediBot retrieval pipeline.

Tests retrieval quality, latency, and index health without requiring LLM API access.
"""

import time
from pathlib import Path

from medibot.config import FAISS_INDEX_PATH
from medibot.vectorstore import load_vectorstore

TEST_QUERIES = [
    {
        "query": "What are the symptoms of hypertension?",
        "keywords": ["blood pressure", "hypertension", "systolic", "diastolic"],
    },
    {
        "query": "How is diabetes diagnosed?",
        "keywords": ["diabetes", "blood glucose", "HbA1c", "fasting"],
    },
    {
        "query": "What causes asthma attacks?",
        "keywords": ["asthma", "airway", "bronchospasm", "triggers"],
    },
    {
        "query": "Treatment options for depression",
        "keywords": ["depression", "antidepressant", "therapy", "SSRI"],
    },
    {
        "query": "What is myocardial infarction?",
        "keywords": ["myocardial", "infarction", "heart attack", "coronary"],
    },
]


def evaluate_index(db):
    print("=" * 60)
    print("INDEX STATISTICS")
    print("=" * 60)

    doc_count = db.index.ntotal
    dim = db.index.d
    print(f"  Total vectors: {doc_count}")
    print(f"  Embedding dimensions: {dim}")
    print(f"  Index path: {FAISS_INDEX_PATH}")

    sample = db.similarity_search("test", k=5)
    chunk_lengths = [len(doc.page_content) for doc in sample]
    print(f"\n  Sample chunk lengths: {chunk_lengths}")


def evaluate_retrieval(db, k=5):
    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION")
    print("=" * 60)

    total_time = 0
    results = []

    for item in TEST_QUERIES:
        start = time.time()
        docs = db.similarity_search(item["query"], k=k)
        elapsed = time.time() - start
        total_time += elapsed

        retrieved_text = " ".join(doc.page_content.lower() for doc in docs)
        hits = sum(1 for kw in item["keywords"] if kw.lower() in retrieved_text)
        hit_rate = hits / len(item["keywords"])

        results.append({
            "query": item["query"],
            "latency_ms": round(elapsed * 1000, 1),
            "docs_returned": len(docs),
            "keyword_hits": f"{hits}/{len(item['keywords'])}",
            "hit_rate": round(hit_rate, 2),
        })

    avg_latency = total_time / len(TEST_QUERIES)

    print(f"\n  {'Query':<45} {'ms':>6} {'Docs':>4} {'Keywords':>10} {'Score':>5}")
    print(f"  {'-'*45} {'-'*6} {'-'*4} {'-'*10} {'-'*5}")

    for r in results:
        print(f"  {r['query'][:44]:<45} {r['latency_ms']:>6} {r['docs_returned']:>4} {r['keyword_hits']:>10} {r['hit_rate']:>5}")

    print(f"\n  Average latency: {avg_latency * 1000:.1f}ms")
    avg_hit_rate = sum(r["hit_rate"] for r in results) / len(results)
    print(f"  Average keyword hit rate: {avg_hit_rate:.0%}")

    return results


def main():
    print("Loading vector store...")
    db = load_vectorstore()

    evaluate_index(db)
    evaluate_retrieval(db, k=5)

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
