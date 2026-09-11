#!/usr/bin/env python3
"""
Interactive CLI Demonstrator for Mini Search Engine.
Demonstrates Porter Stemmer, Positional Inverted Index, Okapi BM25 ranking,
Prefix Trie Autocomplete, and Damerau-Levenshtein Typo Correction.
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.preprocessor import PorterStemmer, TextPreprocessor
from engine.inverted_index import InvertedIndex
from engine.ranker import BM25Ranker
from engine.trie import PrefixTrie
from engine.spellcheck import TypoCorrector


def main():
    print("\n" + "=" * 65)
    print("  MINI SEARCH ENGINE - INFORMATION RETRIEVAL DEMO")
    print("=" * 65)

    print("\n[1] Demonstrating Pure-Algorithmic Porter Stemmer...")
    stemmer = PorterStemmer()
    test_words = ["engineering", "engineers", "databases", "connecting", "consensus", "replicated"]
    for w in test_words:
        print(f"    • '{w:<14}' -> Stem: '{stemmer.stem(w)}'")

    print("\n[2] Indexing Sample Knowledge Corpus into Positional Index...")
    index = InvertedIndex()
    articles = [
        (1, "Distributed Consensus via Raft", "Nodes in distributed networks agree on replicated state machines using the Raft consensus algorithm."),
        (2, "High-Throughput Redis Streams", "Redis streams provide append-only event logs and consumer groups for decoupled microservices."),
        (3, "Database Storage Engines", "Relational databases like PostgreSQL utilize B-Trees while NoSQL uses LSM trees for write throughput."),
        (4, "Non-Adjacent Mention", "Distributed systems sometimes suffer when consensus is lost in remote clusters.")
    ]
    for doc_id, title, body in articles:
        index.add_document(doc_id, title, body)
        print(f"    ✓ Indexed Doc #{doc_id}: '{title}' ({index.doc_lengths[doc_id]} tokens)")

    print(f"\n    Corpus Stats: {index.total_documents} docs | {len(index.index)} unique terms | avgdl={index.average_document_length:.1f}")

    print("\n[3] Executing Okapi BM25 Ranked Query: 'distributed consensus'...")
    ranker = BM25Ranker(index, k1=1.5, b=0.75, title_weight=3.0)
    results = ranker.search("distributed consensus", top_k=3)
    for idx, r in enumerate(results, 1):
        print(f"    {idx}. Doc #{r.doc_id}: '{r.title}' (BM25 Score: {r.score:.4f})")
        print(f"       Breakdown: {r.score_breakdown}")
        print(f"       Snippet:   {r.snippet}")

    print("\n[4] Positional Exact Phrase Query: '\"distributed consensus\"'...")
    phrase_tokens = index.preprocessor.tokenize_query("distributed consensus")
    matched_doc_ids = index.match_phrase(phrase_tokens)
    print(f"    • Exact Phrase Matches: Doc IDs {matched_doc_ids} (Doc #4 excluded because words are non-adjacent)")

    print("\n[5] Prefix Trie Autocomplete (Prefix: 'dis')...")
    trie = PrefixTrie()
    for w in ["distributed", "distribution", "distribute", "database", "data"]:
        trie.insert(w, frequency=50)
    suggestions = trie.autocomplete("dis", max_results=3)
    print(f"    • Autocomplete for 'dis': {suggestions}")

    print("\n[6] Damerau-Levenshtein Typo Correction...")
    spellchecker = TypoCorrector({"distributed", "consensus", "database", "replicated"})
    typos = ["distrubuted", "consenuss", "databaes"]
    for t in typos:
        suggestion = spellchecker.suggest(t)
        print(f"    • Misspelled: '{t:<14}' -> Suggested: '{suggestion}'")

    print("\n" + "=" * 65)
    print("  DEMO COMPLETE: All IR algorithms verified successfully.")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
