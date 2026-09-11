import time
import re
from engine.inverted_index import InvertedIndex
from engine.ranker import BM25Ranker

CORPUS_SIZE = 1500
SAMPLE_TOPICS = [
    ("Consensus in Distributed Networks", "Nodes exchange heartbeats and elect leaders to replicate logs safely across distributed state machines."),
    ("High-Performance Cache Invalidation", "Cache-aside architectures with Redis improve database read throughput but require careful invalidation."),
    ("Asynchronous Message Queues", "Streaming brokers like Apache Kafka and Redis Streams decouple producer services from consumer workers."),
    ("Storage Engines and LSM Trees", "Log Structured Merge trees optimize disk writes using append-only commit logs and sorted string tables."),
    ("Kubernetes Self-Healing Operators", "Control loops reconcile desired state against live cluster state to automate operational workflows.")
]


def run_benchmark():
    print("============================================================")
    print(" Mini Search Engine - Performance & Scalability Benchmark")
    print(f" Generating corpus of {CORPUS_SIZE} synthetic engineering docs")
    print("============================================================")

    index = InvertedIndex()
    raw_docs = []

    for i in range(CORPUS_SIZE):
        topic_title, topic_body = SAMPLE_TOPICS[i % len(SAMPLE_TOPICS)]
        title = f"{topic_title} - Part {i}"
        content = f"{topic_body} Supplementary telemetry metrics and system specifications for node {i}."
        index.add_document(i, title, content)
        raw_docs.append({"id": i, "title": title, "content": content})

    ranker = BM25Ranker(index)
    test_queries = [
        "distributed consensus",
        "redis streams message",
        "lsm trees write",
        "kubernetes operators",
        "cache invalidation"
    ]
    iterations = 200

    # 1. Benchmark Naive Linear Search (regex scan across all docs)
    t0 = time.perf_counter()
    naive_matches = 0
    for _ in range(iterations):
        for q in test_queries:
            pattern = re.compile(rf"\b{re.escape(q.split()[0])}\b", re.IGNORECASE)
            for d in raw_docs:
                if pattern.search(d["title"]) or pattern.search(d["content"]):
                    naive_matches += 1
    linear_time = time.perf_counter() - t0

    # 2. Benchmark Inverted Index + Okapi BM25
    t1 = time.perf_counter()
    bm25_matches = 0
    for _ in range(iterations):
        for q in test_queries:
            results = ranker.search(q, top_k=10)
            bm25_matches += len(results)
    bm25_time = time.perf_counter() - t1

    speedup = linear_time / bm25_time if bm25_time > 0 else 1.0

    print("\n----------------- SEARCH BENCHMARK RESULTS -----------------")
    print(f" Total Query Iterations:    {iterations * len(test_queries)}")
    print(f" Linear Scan Total Time:    {linear_time:.4f} s  (Avg: {(linear_time / (iterations * len(test_queries))) * 1000:.3f} ms/query)")
    print(f" Inverted Index BM25 Time:  {bm25_time:.4f} s  (Avg: {(bm25_time / (iterations * len(test_queries))) * 1000:.3f} ms/query)")
    print(f" Performance Speedup:       {speedup:.1f}x Faster")
    print("------------------------------------------------------------\n")


if __name__ == "__main__":
    run_benchmark()
