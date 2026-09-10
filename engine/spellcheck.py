from typing import Set, Optional, List, Tuple


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes Damerau-Levenshtein distance between two strings.
    Supports insertions, deletions, substitutions, and adjacent transpositions.
    """
    d = {}
    len1 = len(s1)
    len2 = len(s2)

    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,        # deletion
                d[(i, j - 1)] + 1,        # insertion
                d[(i - 1, j - 1)] + cost  # substitution
            )
            # Transposition check
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + 1)

    return d[(len1 - 1, len2 - 1)]


class TypoCorrector:
    """
    Spelling correction and "Did You Mean?" suggestion engine.
    Matches queries against the index vocabulary using edit distance.
    """

    def __init__(self, vocabulary: Optional[Set[str]] = None):
        self.vocabulary = vocabulary or set()

    def update_vocabulary(self, words: Set[str]) -> None:
        self.vocabulary.update(w.lower() for w in words if len(w) > 2)

    def suggest(self, word: str, max_distance: int = 2) -> Optional[str]:
        """Returns the closest vocabulary match within edit distance."""
        word = word.lower().strip()
        if not word or word in self.vocabulary:
            return None

        best_match = None
        min_dist = max_distance + 1

        for vocab_word in self.vocabulary:
            # Quick length filter optimization
            if abs(len(vocab_word) - len(word)) > max_distance:
                continue

            dist = damerau_levenshtein_distance(word, vocab_word)
            if dist < min_dist:
                min_dist = dist
                best_match = vocab_word

        return best_match if min_dist <= max_distance else None
