import os
import json
import time
from contextlib import asynccontextmanager
from typing import Optional, List, Dict
from fastapi import FastAPI, Query, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.config import settings
from engine.preprocessor import TextPreprocessor
from engine.inverted_index import InvertedIndex
from engine.ranker import BM25Ranker
from engine.trie import PrefixTrie
from engine.spellcheck import TypoCorrector

# Global In-Memory Search Engine Components
preprocessor = TextPreprocessor()
index = InvertedIndex(preprocessor)
ranker = BM25Ranker(index, k1=settings.BM25_K1, b=settings.BM25_B, title_weight=settings.TITLE_WEIGHT)
trie = PrefixTrie()
spellchecker = TypoCorrector()


def load_corpus():
    """Seeds the inverted index, trie, and spellchecker with the knowledge corpus."""
    if os.path.exists(settings.CORPUS_PATH):
        with open(settings.CORPUS_PATH, "r", encoding="utf-8") as f:
            articles = json.load(f)

        vocab = set()
        for doc in articles:
            doc_id = doc["id"]
            title = doc["title"]
            content = doc["content"]
            metadata = {
                "category": doc.get("category", "General"),
                "url": doc.get("url", "#")
            }
            index.add_document(doc_id, title, content, metadata)

            # Populate vocabulary for Trie & Spellchecker
            raw_words = f"{title} {content}".split()
            for w in raw_words:
                clean_w = "".join(ch for ch in w if ch.isalnum()).lower()
                if len(clean_w) > 2:
                    trie.insert(clean_w)
                    vocab.add(clean_w)

        spellchecker.update_vocabulary(vocab)
        print(f"[+] Loaded and indexed {len(articles)} documents into Inverted Index.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_corpus()
    yield


app = FastAPI(
    title="Mini Search Engine (BM25 Inverted Index)",
    description="Lucene-style information retrieval search engine with Okapi BM25 ranking and autocomplete.",
    version="1.0.0",
    lifespan=lifespan
)

# Static Files for Web UI
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class DocumentCreate(BaseModel):
    id: int
    title: str
    content: str
    category: Optional[str] = "General"
    url: Optional[str] = "#"


@app.get("/", include_in_schema=False)
async def serve_ui():
    """Serves modern search UI."""
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/api/v1/search", tags=["Search"])
async def search_endpoint(
    q: str = Query(..., description="Query string e.g., 'distributed consensus'"),
    top_k: int = Query(10, ge=1, le=50, description="Max results to return")
):
    """
    Executes full-text query using Okapi BM25 ranking over the Inverted Index.
    Returns relevance-ordered results with execution time and typo correction.
    """
    t0 = time.perf_counter()
    results = ranker.search(q, top_k=top_k)
    duration_ms = (time.perf_counter() - t0) * 1000.0

    # Typo suggestion if query has few/no results
    did_you_mean = None
    query_words = q.strip().split()
    if len(query_words) == 1 and (len(results) == 0 or len(results) < 2):
        correction = spellchecker.suggest(query_words[0])
        if correction and correction.lower() != query_words[0].lower():
            did_you_mean = correction

    return {
        "query": q,
        "execution_time_ms": round(duration_ms, 2),
        "total_results": len(results),
        "did_you_mean": did_you_mean,
        "results": [
            {
                "doc_id": r.doc_id,
                "title": r.title,
                "snippet": r.snippet,
                "score": r.score,
                "score_breakdown": r.score_breakdown,
                "metadata": r.metadata
            }
            for r in results
        ]
    }


@app.get("/api/v1/autocomplete", tags=["Search"])
async def autocomplete_endpoint(
    prefix: str = Query(..., min_length=1, description="Word prefix")
):
    """Returns top search-as-you-type prefix suggestions from Trie."""
    suggestions = trie.autocomplete(prefix, max_results=6)
    return {"prefix": prefix, "suggestions": suggestions}


@app.get("/api/v1/documents", tags=["Documents"])
async def list_documents():
    """Lists all documents stored in the inverted index."""
    return {
        "total_documents": index.total_documents,
        "results": list(index.documents.values())
    }


@app.post("/api/v1/documents", status_code=status.HTTP_201_CREATED, tags=["Documents"])
async def add_document(doc: DocumentCreate):
    """Dynamically indexes a new document into the running search engine."""
    index.add_document(
        doc_id=doc.id,
        title=doc.title,
        content=doc.content,
        metadata={"category": doc.category, "url": doc.url}
    )
    # Update Trie
    for w in f"{doc.title} {doc.content}".split():
        clean_w = "".join(ch for ch in w if ch.isalnum()).lower()
        if len(clean_w) > 2:
            trie.insert(clean_w)
            spellchecker.update_vocabulary({clean_w})

    return {"status": "indexed", "doc_id": doc.id, "title": doc.title}


@app.delete("/api/v1/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Documents"])
async def delete_document(doc_id: int):
    """Deletes a document from the inverted index."""
    if doc_id not in index.documents:
        raise HTTPException(status_code=404, detail="Document not found.")
    index.remove_document(doc_id)


@app.get("/healthz", tags=["Observability"])
async def healthcheck():
    return {
        "status": "UP",
        "documents_indexed": index.total_documents,
        "unique_terms": len(index.index)
    }
