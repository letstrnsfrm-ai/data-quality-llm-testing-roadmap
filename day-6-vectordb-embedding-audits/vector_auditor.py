"""
Vector Database & Embedding Quality Auditor
Implements chunking strategies, TF-IDF vector embeddings, cosine similarity search, and Recall@K benchmarking.
"""
from typing import List, Dict, Any, Tuple
import math
import re

def tokenize(text: str) -> List[str]:
    return [w for w in re.findall(r'\b[a-z0-9_]+\b', text.lower()) if len(w) > 2]

class Chunk:
    def __init__(self, doc_id: str, chunk_index: int, text: str):
        self.doc_id = doc_id
        self.chunk_index = chunk_index
        self.text = text
        self.tokens = tokenize(text)

class VectorAuditor:
    def __init__(self):
        self.chunks: List[Chunk] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def chunk_document(self, doc_id: str, text: str, chunk_size: int = 25, overlap: int = 5) -> List[Chunk]:
        words = text.split()
        chunks: List[Chunk] = []
        start = 0
        idx = 0
        step = max(1, chunk_size - overlap)

        while start < len(words):
            end = min(len(words), start + chunk_size)
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)
            chunks.append(Chunk(doc_id=doc_id, chunk_index=idx, text=chunk_text))
            idx += 1
            if end == len(words):
                break
            start += step

        return chunks

    def index_documents(self, docs: List[Dict[str, Any]], chunk_size: int = 25, overlap: int = 5):
        self.chunks = []
        for doc in docs:
            doc_chunks = self.chunk_document(doc["id"], doc["content"], chunk_size=chunk_size, overlap=overlap)
            self.chunks.extend(doc_chunks)

        # Build vocabulary & compute IDF
        doc_freq: Dict[str, int] = {}
        for chunk in self.chunks:
            unique_tokens = set(chunk.tokens)
            for token in unique_tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

        total_chunks = max(1, len(self.chunks))
        self.vocabulary = {term: idx for idx, term in enumerate(doc_freq.keys())}
        self.idf = {term: math.log((total_chunks + 1) / (df + 1)) + 1.0 for term, df in doc_freq.items()}

    def _embed(self, tokens: List[str]) -> Dict[str, float]:
        tf: Dict[str, int] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1

        vec: Dict[str, float] = {}
        for t, count in tf.items():
            if t in self.idf:
                vec[t] = count * self.idf[t]

        # Normalize L2
        norm = math.sqrt(sum(v * v for v in vec.values()))
        if norm > 0:
            for t in vec:
                vec[t] /= norm

        return vec

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        score = 0.0
        for t, val1 in vec1.items():
            if t in vec2:
                score += val1 * vec2[t]
        return min(1.0, max(0.0, score))

    def search(self, query: str, top_k: int = 3) -> List[Tuple[Chunk, float]]:
        q_tokens = tokenize(query)
        q_vec = self._embed(q_tokens)

        results: List[Tuple[Chunk, float]] = []
        for chunk in self.chunks:
            c_vec = self._embed(chunk.tokens)
            sim = self._cosine_similarity(q_vec, c_vec)
            results.append((chunk, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def benchmark_recall_at_k(self, queries: List[Dict[str, Any]], top_k: int = 3) -> float:
        if not queries:
            return 0.0

        hits = 0
        for q in queries:
            results = self.search(q["query"], top_k=top_k)
            retrieved_doc_ids = set(chunk.doc_id for chunk, _ in results)
            if q["expected_doc_id"] in retrieved_doc_ids:
                hits += 1

        return hits / len(queries)
