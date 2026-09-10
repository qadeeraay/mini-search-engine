import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from engine.preprocessor import TextPreprocessor


@dataclass
class Posting:
    doc_id: int
    term_frequency: int = 0
    positions: List[int] = field(default_factory=list)


class InvertedIndex:
    """
    Positional Inverted Index with document length tracking and phrase query support.
    Maps: Term -> { DocID: Posting(tf, [positions]) }
    """

    def __init__(self, preprocessor: Optional[TextPreprocessor] = None):
        self.preprocessor = preprocessor or TextPreprocessor()
        # term -> { doc_id: Posting }
        self.index: Dict[str, Dict[int, Posting]] = {}
        # doc_id -> total token count (for BM25 length normalization)
        self.doc_lengths: Dict[int, int] = {}
        # doc_id -> raw document payload
        self.documents: Dict[int, dict] = {}
        self.total_tokens: int = 0

    @property
    def total_documents(self) -> int:
        return len(self.documents)

    @property
    def average_document_length(self) -> float:
        if not self.documents:
            return 0.0
        return self.total_tokens / len(self.documents)

    def add_document(self, doc_id: int, title: str, content: str, metadata: Optional[dict] = None) -> None:
        """
        Indexes a document into the positional inverted index.
        Applies title weighting by artificially prepending title tokens.
        """
        # Remove existing if overwriting
        if doc_id in self.documents:
            self.remove_document(doc_id)

        full_text = f"{title} {content}"
        tokens_with_positions = self.preprocessor.process(full_text)
        doc_length = len(tokens_with_positions)

        self.doc_lengths[doc_id] = doc_length
        self.total_tokens += doc_length
        self.documents[doc_id] = {
            "id": doc_id,
            "title": title,
            "content": content,
            "metadata": metadata or {}
        }

        # Build positional postings
        for term, pos in tokens_with_positions:
            if term not in self.index:
                self.index[term] = {}

            if doc_id not in self.index[term]:
                self.index[term][doc_id] = Posting(doc_id=doc_id, term_frequency=0, positions=[])

            posting = self.index[term][doc_id]
            posting.term_frequency += 1
            posting.positions.append(pos)

    def remove_document(self, doc_id: int) -> None:
        """Removes a document from the inverted index and updates metrics."""
        if doc_id not in self.documents:
            return

        doc_length = self.doc_lengths.pop(doc_id, 0)
        self.total_tokens -= doc_length
        self.documents.pop(doc_id, None)

        terms_to_clean = []
        for term, postings in self.index.items():
            if doc_id in postings:
                del postings[doc_id]
                if not postings:
                    terms_to_clean.append(term)

        for term in terms_to_clean:
            del self.index[term]

    def get_document_frequency(self, term: str) -> int:
        """Returns number of documents containing term: n(q_i)."""
        return len(self.index.get(term, {}))

    def get_term_frequency(self, term: str, doc_id: int) -> int:
        """Returns frequency of term within specific document: f(q_i, D)."""
        postings = self.index.get(term, {})
        if doc_id in postings:
            return postings[doc_id].term_frequency
        return 0

    def match_phrase(self, phrase_terms: List[str]) -> Set[int]:
        """
        Evaluates exact phrase queries (e.g., 'distributed systems')
        by verifying adjacent token positions in identical documents.
        """
        if not phrase_terms:
            return set()

        first_term = phrase_terms[0]
        if first_term not in self.index:
            return set()

        candidate_docs = set(self.index[first_term].keys())
        for term in phrase_terms[1:]:
            if term not in self.index:
                return set()
            candidate_docs.intersection_update(self.index[term].keys())

        matched_docs = set()
        for doc_id in candidate_docs:
            # Check if positional sequence exists: pos[i+1] == pos[i] + 1
            first_positions = self.index[first_term][doc_id].positions
            for start_pos in first_positions:
                found_match = True
                for offset, next_term in enumerate(phrase_terms[1:], start=1):
                    target_pos = start_pos + offset
                    if target_pos not in self.index[next_term][doc_id].positions:
                        found_match = False
                        break
                if found_match:
                    matched_docs.add(doc_id)
                    break

        return matched_docs

    def serialize(self) -> str:
        """Serializes index state to JSON string."""
        serializable_index = {}
        for term, postings in self.index.items():
            serializable_index[term] = {
                str(doc_id): {"tf": p.term_frequency, "pos": p.positions}
                for doc_id, p in postings.items()
            }
        payload = {
            "documents": self.documents,
            "doc_lengths": {str(k): v for k, v in self.doc_lengths.items()},
            "total_tokens": self.total_tokens,
            "index": serializable_index
        }
        return json.dumps(payload)

    def deserialize(self, json_str: str) -> None:
        """Restores index state from JSON string."""
        payload = json.loads(json_str)
        self.documents = {int(k): v for k, v in payload["documents"].items()}
        self.doc_lengths = {int(k): v for k, v in payload["doc_lengths"].items()}
        self.total_tokens = payload["total_tokens"]
        self.index = {}

        for term, postings in payload["index"].items():
            self.index[term] = {}
            for doc_id_str, pdata in postings.items():
                doc_id = int(doc_id_str)
                self.index[term][doc_id] = Posting(
                    doc_id=doc_id,
                    term_frequency=pdata["tf"],
                    positions=pdata["pos"]
                )
