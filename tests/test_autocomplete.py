import unittest
from engine.trie import PrefixTrie
from engine.spellcheck import TypoCorrector, damerau_levenshtein_distance


class TestAutocompleteAndSpellcheck(unittest.TestCase):
    def test_trie_prefix_autocomplete(self):
        trie = PrefixTrie()
        trie.insert("distributed", frequency=100)
        trie.insert("distribution", frequency=40)
        trie.insert("database", frequency=80)
        trie.insert("data", frequency=90)

        suggestions = trie.autocomplete("dist")
        self.assertEqual(suggestions[0], "distributed")
        self.assertEqual(suggestions[1], "distribution")
        self.assertNotIn("database", suggestions)

    def test_damerau_levenshtein_distance(self):
        # Identical
        self.assertEqual(damerau_levenshtein_distance("raft", "raft"), 0)
        # 1 deletion
        self.assertEqual(damerau_levenshtein_distance("raft", "rat"), 1)
        # 1 insertion
        self.assertEqual(damerau_levenshtein_distance("raft", "draft"), 1)
        # 1 substitution
        self.assertEqual(damerau_levenshtein_distance("raft", "saft"), 1)
        # 1 transposition
        self.assertLessEqual(damerau_levenshtein_distance("consensus", "consenuss"), 2)

    def test_typo_corrector_suggestion(self):
        vocab = {"distributed", "consensus", "database", "pipeline"}
        corrector = TypoCorrector(vocab)

        # Typo: 'distrubuted' -> 'distributed'
        suggestion = corrector.suggest("distrubuted")
        self.assertEqual(suggestion, "distributed")

        # Typo: 'consensu' -> 'consensus'
        suggestion2 = corrector.suggest("consensu")
        self.assertEqual(suggestion2, "consensus")


if __name__ == "__main__":
    unittest.main()
