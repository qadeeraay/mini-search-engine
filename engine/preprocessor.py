import re
import unicodedata
from typing import List, Tuple

# Comprehensive English Stopwords
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who",
    "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

WORD_PATTERN = re.compile(r"[a-zA-Z0-9]+(?:'[a-zA-Z0-9]+)?")


class PorterStemmer:
    """
    Self-contained algorithmic implementation of the Porter Stemmer (Martin Porter, 1980).
    Normalizes morphological variants of English words to their base stem.
    """

    def is_consonant(self, word: str, i: int) -> bool:
        c = word[i]
        if c in "aeiou":
            return False
        if c == 'y':
            if i == 0:
                return True
            return not self.is_consonant(word, i - 1)
        return True

    def get_measure(self, word: str) -> int:
        """Returns the measure m of form [C](VC)^m[V]."""
        m = 0
        i = 0
        length = len(word)
        while i < length and self.is_consonant(word, i):
            i += 1
        while i < length:
            while i < length and not self.is_consonant(word, i):
                i += 1
            if i >= length:
                break
            while i < length and self.is_consonant(word, i):
                i += 1
            m += 1
        return m

    def contains_vowel(self, word: str) -> bool:
        for i in range(len(word)):
            if not self.is_consonant(word, i):
                return True
        return False

    def ends_double_consonant(self, word: str) -> bool:
        if len(word) < 2:
            return False
        return word[-1] == word[-2] and self.is_consonant(word, len(word) - 1)

    def cvc(self, word: str) -> bool:
        """Tests if word ends in consonant-vowel-consonant, where final is not w, x, y."""
        if len(word) < 3:
            return False
        i = len(word) - 1
        return (self.is_consonant(word, i) and
                not self.is_consonant(word, i - 1) and
                self.is_consonant(word, i - 2) and
                word[i] not in "wxy")

    def stem(self, word: str) -> str:
        word = word.lower()
        if len(word) <= 2:
            return word

        # Plural and past-participle normalization (phase 1a)
        if word.endswith("sses"):
            word = word[:-2]
        elif word.endswith("ies"):
            word = word[:-2]
        elif not word.endswith("ss") and word.endswith("s"):
            word = word[:-1]

        # Suffix reduction for -eed, -ed, and -ing (phase 1b)
        extra = False
        if word.endswith("eed"):
            stem = word[:-3]
            if self.get_measure(stem) > 0:
                word = stem + "ee"
        elif word.endswith("ed"):
            stem = word[:-2]
            if self.contains_vowel(stem):
                word = stem
                extra = True
        elif word.endswith("ing"):
            stem = word[:-3]
            if self.contains_vowel(stem):
                word = stem
                extra = True

        if extra:
            if word.endswith("at") or word.endswith("bl") or word.endswith("iz"):
                word += "e"
            elif self.ends_double_consonant(word) and word[-1] not in "lsz":
                word = word[:-1]
            elif self.get_measure(word) == 1 and self.cvc(word):
                word += "e"

        # Terminal y to i replacement (phase 1c)
        if word.endswith("y") and self.contains_vowel(word[:-1]):
            word = word[:-1] + "i"

        # Derivational suffix mapping (phases 2 and 3)
        step2_map = {
            "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance",
            "izer": "ize", "bli": "ble", "alli": "al", "entli": "ent",
            "eli": "e", "ousli": "ous", "ization": "ize", "ation": "ate",
            "ator": "ate", "alism": "al", "iveness": "ive", "fulness": "ful",
            "ousness": "ous", "aliti": "al", "iviti": "ive", "biliti": "ble"
        }
        for suffix, replacement in step2_map.items():
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self.get_measure(stem) > 0:
                    word = stem + replacement
                break

        # Residual suffix stripping (phase 4)
        step4_suffixes = ["al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement", "ment", "ent", "ou", "ism", "ate", "iti", "ous", "ive", "ize"]
        for suffix in step4_suffixes:
            if word.endswith(suffix):
                stem = word[:-len(suffix)]
                if self.get_measure(stem) > 1:
                    word = stem
                break

        # Terminal e and double consonant normalization (phase 5)
        if word.endswith("e"):
            stem = word[:-1]
            m = self.get_measure(stem)
            if m > 1 or (m == 1 and not self.cvc(stem)):
                word = stem

        if self.get_measure(word) > 1 and self.ends_double_consonant(word) and word.endswith("l"):
            word = word[:-1]

        return word


class TextPreprocessor:
    """
    NLP Text Preprocessing Pipeline:
    - Normalizes unicode
    - Extracts alphanumeric tokens with positional tracking
    - Filters stopwords
    - Applies Porter Stemming
    """

    def __init__(self, remove_stopwords: bool = True, stem_words: bool = True):
        self.remove_stopwords = remove_stopwords
        self.stem_words = stem_words
        self.stemmer = PorterStemmer()

    def process(self, text: str) -> List[Tuple[str, int]]:
        """
        Tokenizes text, returning a list of (stemmed_token, position) tuples.
        Position is preserved for exact phrase matching.
        """
        if not text:
            return []

        # Unicode normalization
        normalized = unicodedata.normalize("NFKD", text)
        raw_tokens = WORD_PATTERN.findall(normalized)

        processed = []
        for pos, token in enumerate(raw_tokens):
            clean_token = token.lower()
            if self.remove_stopwords and clean_token in STOPWORDS:
                continue
            if len(clean_token) < 2:
                continue
            if self.stem_words:
                clean_token = self.stemmer.stem(clean_token)
            processed.append((clean_token, pos))

        return processed

    def tokenize_query(self, query: str) -> List[str]:
        """Processes query terms identically to indexed documents."""
        tokens_with_pos = self.process(query)
        return [t[0] for t in tokens_with_pos]
