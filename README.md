# Inverted Index & Okapi BM25 Mini Search Engine

[![CI Pipeline](https://github.com/qadeeraay/mini-search-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/qadeeraay/mini-search-engine/actions/workflows/ci.yml)
[![CodeQL Security](https://github.com/qadeeraay/mini-search-engine/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/qadeeraay/mini-search-engine/actions/workflows/codeql-analysis.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Information Retrieval](https://img.shields.io/badge/Algorithms-BM25%20%7C%20Trie-purple.svg)](https://en.wikipedia.org/wiki/Okapi_BM25)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg)](https://www.docker.com/)

A full-text search engine engineered from scratch in Python, implementing the core information retrieval algorithms that power Apache Lucene and Elasticsearch: a positional inverted index, the Okapi BM25 ranking algorithm, a Prefix Trie for autocomplete, and Damerau-Levenshtein typo correction.

---

## System Design & Algorithmic Highlights

- **Positional Inverted Index:** Engineered a custom index tracking document IDs, term frequencies, and word offsets, enabling exact phrase queries (`"distributed systems"`) in $O(P)$ time without rescanning document text.
- **Pure-Algorithmic Text Preprocessing:** Implemented the classic **Porter Stemming Algorithm (1980)** and a regex tokenization pipeline without third-party NLP library dependencies.
- **Okapi BM25 Relevance Scoring:** Implemented the industry-standard BM25 ranking function with tunable term frequency saturation ($k_1=1.5$) and document length normalization ($b=0.75$), plus multi-field weighting ($3\times$ title boost).
- **Prefix Trie Autocomplete:** $O(L)$ search-as-you-type suggestion engine prioritizing terms by corpus frequency.
- **Damerau-Levenshtein Typo Correction:** Dynamic programming string distance providing "Did you mean?" suggestions for misspelled queries.
- **Modern Responsive Web UI:** Fast, dark-mode web application featuring real-time search, execution latency telemetry in milliseconds, highlighted excerpts, and BM25 score breakdowns.

---

## Quickstart Guide

### 1. Run with Docker
```bash
docker compose up -d --build
```
Open your browser at `http://localhost:8003` to interact with the search UI.

### 2. Local Setup
```bash
make setup
make run
```
Access the interactive web UI at `http://localhost:8003`.

---

## REST API Specification

### 1. Search Query
```bash
curl "http://localhost:8003/api/v1/search?q=consensus&top_k=5"
```
**Response (HTTP 200):**
```json
{
  "query": "consensus",
  "execution_time_ms": 0.42,
  "total_results": 2,
  "did_you_mean": null,
  "results": [
    {
      "doc_id": 1,
      "title": "Understanding Distributed Consensus and the Raft Algorithm",
      "snippet": "Distributed consensus is the protocol by which multiple nodes in a distributed system agree on a shared state machine. The Raft consensus algorithm was designed as a more understandable alternative...",
      "score": 4.1824,
      "score_breakdown": { "consensus": 4.1824 },
      "metadata": { "category": "Distributed Systems", "url": "https://raft.github.io/" }
    }
  ]
}
```

### 2. Autocomplete Suggestions
```bash
curl "http://localhost:8003/api/v1/autocomplete?prefix=dist"
```
**Response (HTTP 200):**
```json
{
  "prefix": "dist",
  "suggestions": ["distributed", "distribution", "distribute"]
}
```

---

## Performance & Scalability Benchmark

Run the automated benchmark comparing the Inverted Index BM25 search vs linear regex scanning:
```bash
python scripts/benchmark_search.py
```

**Benchmark Results (1,500 documents, 1,000 query iterations):**
```
----------------- SEARCH BENCHMARK RESULTS -----------------
 Total Query Iterations:    1,000
 Linear Scan Total Time:    1.2480 s  (Avg: 1.248 ms/query)
 Inverted Index BM25 Time:  0.0284 s  (Avg: 0.028 ms/query)
 Performance Speedup:       43.9x Faster
------------------------------------------------------------
```

---

## Algorithmic Capabilities & Benchmark Specifications

Key algorithmic capabilities and computational benchmarks:

> - *"Full-text search engine engineered from scratch in Python featuring a Positional Inverted Index and Okapi BM25 relevance ranking, achieving a 44x query speedup over linear scans on benchmark datasets."*
> - *"NLP preprocessing pipeline including a custom Porter Stemming algorithm and positional token sequencer supporting exact multi-term phrase queries in sub-millisecond execution times."*
> - *"Prefix Trie autocomplete engine and Damerau-Levenshtein typo correction algorithm, delivering sub-millisecond search-as-you-type suggestions through a modern FastAPI web interface."*
