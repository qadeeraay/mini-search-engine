import math
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from engine.inverted_index import InvertedIndex


@dataclass
class SearchResult:
    doc_id: int
    title: str
    content: str
    snippet: str
    score: float
    score_breakdown: Dict[str, float]
    metadata: dict


class BM25Ranker:
    """
    Okapi BM25 Relevance Ranking Algorithm.
    The mathematical standard used by Apache Lucene and Elasticsearch.
    
    Formula:
    IDF(q_i) = ln( (N - n(q_i) + 0.5) / (n(q_i) + 0.5) + 1 )
    Score(D, Q) = sum( IDF(q_i) * ( f(q_i, D) * (k1 + 1) ) / ( f(q_i, D) + k1 * (1 - b + b * (|D| / avgdl)) ) )
    """

    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75, title_weight: float = 3.0):
        self.index = index
        self.k1 = k1
        self.b = b
        self.title_weight = title_weight

    def calculate_idf(self, term: str) -> float:
        """
        Calculates Probabilistic Inverse Document Frequency (Robertson-Spärck Jones IDF).
        Includes smoothing to prevent negative values on terms appearing in >50% of docs.
        """
        N = self.index.total_documents
        n_q = self.index.get_document_frequency(term)
        if n_q == 0:
            return 0.0

        return math.log((N - n_q + 0.5) / (n_q + 0.5) + 1.0)

    def search(self, query: str, top_k: int = 10, exact_phrase: bool = False) -> List[SearchResult]:
        """
        Executes search query across inverted index and ranks documents via Okapi BM25.
        """
        if not query.strip() or self.index.total_documents == 0:
            return []

        # Check for quoted exact phrase queries: "distributed systems"
        phrase_matches = re.findall(r'"([^"]*)"', query)
        terms = self.index.preprocessor.tokenize_query(query)

        if not terms:
            return []

        avgdl = self.index.average_document_length
        if avgdl == 0:
            return []

        # Collect candidate documents containing at least one query term
        candidate_doc_ids = set()
        for term in terms:
            if term in self.index.index:
                candidate_doc_ids.update(self.index.index[term].keys())

        # If exact phrase query is active, filter candidates
        if phrase_matches or exact_phrase:
            phrase_str = phrase_matches[0] if phrase_matches else query
            phrase_tokens = [t[0] for t in self.index.preprocessor.process(phrase_str)]
            if len(phrase_tokens) > 1:
                matched_phrase_docs = self.index.match_phrase(phrase_tokens)
                if matched_phrase_docs:
                    candidate_doc_ids.intersection_update(matched_phrase_docs)

        if not candidate_doc_ids:
            return []

        scores: Dict[int, float] = {}
        score_breakdowns: Dict[int, Dict[str, float]] = {}

        for doc_id in candidate_doc_ids:
            D_len = self.index.doc_lengths.get(doc_id, 1)
            doc_score = 0.0
            breakdown = {}

            doc_info = self.index.documents[doc_id]
            title_terms = set(self.index.preprocessor.tokenize_query(doc_info["title"]))

            for term in terms:
                f_qD = self.index.get_term_frequency(term, doc_id)
                if f_qD == 0:
                    continue

                idf = self.calculate_idf(term)
                # BM25 Term Frequency Saturation & Length Normalization
                numerator = f_qD * (self.k1 + 1.0)
                denominator = f_qD + self.k1 * (1.0 - self.b + self.b * (D_len / avgdl))
                term_score = idf * (numerator / denominator)

                # Title Match Relevance Multiplier
                if term in title_terms:
                    term_score *= self.title_weight

                doc_score += term_score
                breakdown[term] = round(term_score, 4)

            scores[doc_id] = doc_score
            score_breakdowns[doc_id] = breakdown

        # Sort documents by BM25 score in descending order
        sorted_doc_ids = sorted(scores.keys(), key=lambda did: scores[did], reverse=True)[:top_k]

        results = []
        for doc_id in sorted_doc_ids:
            doc = self.index.documents[doc_id]
            snippet = self._generate_snippet(doc["content"], terms)
            results.append(SearchResult(
                doc_id=doc_id,
                title=doc["title"],
                content=doc["content"],
                snippet=snippet,
                score=round(scores[doc_id], 4),
                score_breakdown=score_breakdowns[doc_id],
                metadata=doc.get("metadata", {})
            ))

        return results

    def _generate_snippet(self, content: str, query_terms: List[str], max_words: int = 35) -> str:
        """Generates an excerpt snippet with highlighted keyword matches."""
        words = content.split()
        if len(words) <= max_words:
            return content

        # Find first occurrence of any query root term
        best_start = 0
        stemmer = self.index.preprocessor.stemmer
        query_roots = set(query_terms)

        for idx, word in enumerate(words):
            clean_word = stemmer.stem(re.sub(r"[^\w]", "", word.lower()))
            if clean_word in query_roots:
                best_start = max(0, idx - 5)
                break

        excerpt = words[best_start:best_start + max_words]
        snippet_text = " ".join(excerpt)
        if best_start > 0:
            snippet_text = f"...{snippet_text}"
        if best_start + max_words < len(words):
            snippet_text = f"{snippet_text}..."

        return snippet_text
