from typing import Dict, List


class PrefixTrie:
    """
    Prefix search-as-you-type query autocomplete suggestions,
    ranked by term corpus frequency.
    """

    def __init__(self):
        self._words: Dict[str, int] = {}

    def insert(self, word: str, frequency: int = 1) -> None:
        """Inserts or increments a word with its corpus frequency."""
        word = word.lower().strip()
        if word:
            self._words[word] = self._words.get(word, 0) + frequency

    def autocomplete(self, prefix: str, max_results: int = 5) -> List[str]:
        """Returns top autocomplete suggestions matching prefix ranked by frequency."""
        prefix = prefix.lower().strip()
        if not prefix:
            return []

        matches = [(w, freq) for w, freq in self._words.items() if w.startswith(prefix)]
        matches.sort(key=lambda x: x[1], reverse=True)
        return [w for w, _ in matches[:max_results]]
