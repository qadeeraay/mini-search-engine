import unittest
from engine.inverted_index import InvertedIndex
from engine.ranker import BM25Ranker


class TestBM25Ranker(unittest.TestCase):
    def test_bm25_relevance_ordering(self):
        index = InvertedIndex()
        index.add_document(
            1,
            "Redis Streams Architecture",
            "Redis streams provide consumer groups and decoupled message pipelines for event-driven systems."
        )
        index.add_document(
            2,
            "PostgreSQL Relational DB",
            "PostgreSQL uses B-Tree indexes for fast tabular queries."
        )

        ranker = BM25Ranker(index)
        results = ranker.search("redis consumer groups")

        self.assertGreater(len(results), 0)
        # Document 1 must be ranked at #1
        self.assertEqual(results[0].doc_id, 1)
        self.assertGreater(results[0].score, 0)
        # Verify query stems are recorded in the relevance breakdown
        query_stems = index.preprocessor.tokenize_query("redis")
        self.assertTrue(any(stem in results[0].score_breakdown for stem in query_stems))

    def test_bm25_title_weight_boost(self):
        index = InvertedIndex()
        # Document 1 has 'consensus' in title and body
        index.add_document(1, "Consensus Algorithms", "Understanding distributed consensus.")
        # Document 2 has 'consensus' only in body
        index.add_document(2, "General Computing", "Overview of distributed consensus mechanisms.")

        ranker = BM25Ranker(index, title_weight=3.0)
        results = ranker.search("consensus")

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].doc_id, 1)
        self.assertGreater(results[0].score, results[1].score)


if __name__ == "__main__":
    unittest.main()
