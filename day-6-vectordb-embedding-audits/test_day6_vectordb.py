"""
Day 6 Test Suite: Vector Database & Embedding Validation
Audits vector search recall, chunk overlap effects, and ranking quality.
"""
import unittest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vector_auditor import VectorAuditor

class TestDay6VectorDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus_path = os.path.join(os.path.dirname(__file__), "corpus.json")
        with open(corpus_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.auditor = VectorAuditor()
        cls.auditor.index_documents(cls.data["documents"], chunk_size=30, overlap=10)

    def test_top_k_recall_exceeds_threshold(self):
        queries = self.data["queries"]
        recall_at_3 = self.auditor.benchmark_recall_at_k(queries, top_k=3)
        self.assertGreaterEqual(
            recall_at_3, 0.85,
            f"Recall@3 ({recall_at_3}) fell below expected enterprise SLA threshold of 0.85"
        )
        self.assertEqual(recall_at_3, 1.0)

    def test_cosine_similarity_bounds_and_ranking(self):
        query = "How does token refresh work in OAuth2?"
        results = self.auditor.search(query, top_k=3)

        self.assertGreater(len(results), 0)
        # Verify scores are bounded [0.0, 1.0] and sorted descending
        for i in range(len(results) - 1):
            score_current = results[i][1]
            score_next = results[i + 1][1]
            self.assertGreaterEqual(score_current, score_next)
            self.assertGreaterEqual(score_current, 0.0)
            self.assertLessEqual(score_current, 1.0)

        # Top hit must be the OAuth2 document
        top_chunk, top_score = results[0]
        self.assertEqual(top_chunk.doc_id, "doc_auth_01")
        self.assertGreater(top_score, 0.3)

    def test_overlapping_chunking_creates_continuity(self):
        doc = self.data["documents"][0]
        chunks = self.auditor.chunk_document(doc["id"], doc["content"], chunk_size=15, overlap=5)
        self.assertGreater(len(chunks), 1)

        # Verify chunk 1 and chunk 2 share tokens due to overlap
        overlap_tokens = set(chunks[0].tokens).intersection(set(chunks[1].tokens))
        self.assertGreater(len(overlap_tokens), 0)

if __name__ == "__main__":
    unittest.main()
