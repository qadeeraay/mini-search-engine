import unittest
from engine.inverted_index import InvertedIndex


class TestInvertedIndex(unittest.TestCase):
    def test_inverted_index_insertion_and_lookup(self):
        index = InvertedIndex()
        index.add_document(1, "PostgreSQL Indexing", "B-Tree indexes provide fast logarithmic lookups.")
        index.add_document(2, "LSM Trees", "Log structured merge trees are optimized for fast writes.")

        self.assertEqual(index.total_documents, 2)
        self.assertEqual(index.get_document_frequency("tree"), 2)
        self.assertEqual(index.get_document_frequency("postgresql"), 1)
        self.assertGreaterEqual(index.get_term_frequency("tree", 1), 1)
        self.assertGreaterEqual(index.get_term_frequency("tree", 2), 1)

    def test_phrase_query_matching(self):
        index = InvertedIndex()
        index.add_document(1, "Distributed Consensus", "Nodes reach distributed consensus via the Raft protocol.")
        index.add_document(2, "Non-adjacent terms", "Distributed systems need consensus protocols.")

        # Query: 'distributed consensus' (adjacent words tokenized & stemmed)
        phrase_stems = index.preprocessor.tokenize_query("distributed consensus")
        matched_docs = index.match_phrase(phrase_stems)
        self.assertIn(1, matched_docs)
        # Document 2 has terms separated by 'systems', so phrase match should not trigger
        self.assertNotIn(2, matched_docs)

    def test_remove_document(self):
        index = InvertedIndex()
        index.add_document(1, "Raft", "Leader election protocol.")
        self.assertEqual(index.total_documents, 1)
        index.remove_document(1)
        self.assertEqual(index.total_documents, 0)
        self.assertEqual(index.get_document_frequency("raft"), 0)


if __name__ == "__main__":
    unittest.main()
