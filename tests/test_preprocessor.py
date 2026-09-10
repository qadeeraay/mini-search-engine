import unittest
from engine.preprocessor import PorterStemmer, TextPreprocessor


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.stemmer = PorterStemmer()
        self.preprocessor = TextPreprocessor(remove_stopwords=True, stem_words=True)

    def test_porter_stemmer_rules(self):
        self.assertEqual(self.stemmer.stem("engineering"), "engin")
        self.assertEqual(self.stemmer.stem("engineers"), "engin")
        self.assertEqual(self.stemmer.stem("connected"), "connect")
        self.assertEqual(self.stemmer.stem("connecting"), "connect")
        self.assertEqual(self.stemmer.stem("databases"), "databas")
        self.assertEqual(self.stemmer.stem("queries"), "queri")

    def test_preprocessor_stopwords_and_positions(self):
        text = "The distributed consensus protocol in systems"
        tokens = self.preprocessor.process(text)

        words = [t[0] for t in tokens]
        # 'the' and 'in' should be filtered as stopwords
        self.assertNotIn("the", words)
        self.assertNotIn("in", words)

        # Check that positions are strictly monotonic
        positions = [t[1] for t in tokens]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
