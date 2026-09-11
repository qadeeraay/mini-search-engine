from typing import Dict, List, Tuple


class TrieNode:
    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_word: bool = False
        self.frequency: int = 0


class PrefixTrie:
    """
    Prefix Trie supporting O(L) search-as-you-type query autocomplete suggestions,
    ranked by term corpus frequency.
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, frequency: int = 1) -> None:
        """Inserts a word into the Trie with its corpus frequency."""
        word = word.lower().strip()
        if not word:
            return

        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        node.is_word = True
        node.frequency += frequency

    def autocomplete(self, prefix: str, max_results: int = 5) -> List[str]:
        """Returns top autocomplete suggestions matching prefix."""
        prefix = prefix.lower().strip()
        if not prefix:
            return []

        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        # Depth-First Search to collect all matching words
        matches: List[Tuple[str, int]] = []

        def dfs(current_node: TrieNode, current_prefix: str):
            if current_node.is_word:
                matches.append((current_prefix, current_node.frequency))
            for char, next_node in current_node.children.items():
                dfs(next_node, current_prefix + char)

        dfs(node, prefix)
        # Sort by popularity frequency in descending order
        matches.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in matches[:max_results]]
