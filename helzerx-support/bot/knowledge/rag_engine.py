"""
HELZERX AI Support - Retrieval Augmented Generation (RAG) Engine
Indexes and ranks verified technical documentation, FAQs, and hosting guides.
"""
from __future__ import annotations

import re
import math
from typing import List, Dict, Any, Tuple


class DocumentChunk:
    def __init__(self, title: str, category: str, content: str, chunk_index: int = 0):
        self.title = title
        self.category = category
        self.content = content
        self.chunk_index = chunk_index

    def __repr__(self) -> str:
        return f"<DocumentChunk {self.title} #{self.chunk_index}>"


def chunk_document(title: str, category: str, full_text: str, max_chunk_words: int = 250) -> List[DocumentChunk]:
    """Splits markdown or text documents into semantic chunks preserving headings."""
    paragraphs = full_text.split("\n\n")
    chunks: List[DocumentChunk] = []
    current_chunk: List[str] = []
    current_word_count = 0

    for para in paragraphs:
        words = para.split()
        if not words:
            continue

        if current_word_count + len(words) > max_chunk_words and current_chunk:
            chunks.append(DocumentChunk(
                title=title,
                category=category,
                content="\n\n".join(current_chunk),
                chunk_index=len(chunks)
            ))
            current_chunk = [para]
            current_word_count = len(words)
        else:
            current_chunk.append(para)
            current_word_count += len(words)

    if current_chunk:
        chunks.append(DocumentChunk(
            title=title,
            category=category,
            content="\n\n".join(current_chunk),
            chunk_index=len(chunks)
        ))

    return chunks


def score_chunk_relevance(query: str, chunk: DocumentChunk) -> float:
    """
    Computes BM25-inspired term frequency and title overlap score between query and document chunk.
    """
    query_terms = set(re.findall(r"\w+", query.lower()))
    if not query_terms:
        return 0.0

    content_words = re.findall(r"\w+", chunk.content.lower())
    title_words = set(re.findall(r"\w+", chunk.title.lower()))
    category_words = set(re.findall(r"\w+", chunk.category.lower()))

    score = 0.0

    # Title match gives strong boost
    title_matches = len(query_terms.intersection(title_words))
    score += title_matches * 4.0

    # Category match gives boost
    cat_matches = len(query_terms.intersection(category_words))
    score += cat_matches * 2.5

    # Content term frequency
    content_freq = {}
    for w in content_words:
        content_freq[w] = content_freq.get(w, 0) + 1

    for term in query_terms:
        if term in content_freq:
            tf = content_freq[term]
            # sub-linear term frequency
            score += 1.0 + math.log(tf)

    return score


class RAGEngine:
    """In-memory fast knowledge index for ticket context augmentation."""

    def __init__(self):
        self.chunks: List[DocumentChunk] = []

    def index_document(self, title: str, category: str, content: str) -> None:
        new_chunks = chunk_document(title, category, content)
        self.chunks.extend(new_chunks)

    def search(self, query: str, top_k: int = 3, min_score: float = 1.0) -> List[Tuple[DocumentChunk, float]]:
        """Finds top k most relevant document chunks for the query."""
        scored: List[Tuple[DocumentChunk, float]] = []
        for chunk in self.chunks:
            s = score_chunk_relevance(query, chunk)
            if s >= min_score:
                scored.append((chunk, round(s, 2)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
