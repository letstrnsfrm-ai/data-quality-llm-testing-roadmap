"""
Day 3 Test Suite: Retrieval-Augmented Generation (RAG) Evaluation
Tests Faithfulness, Context Precision, Context Recall, and Answer Relevancy against benchmark datasets.
"""
import unittest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rag_evaluator import RAGEvaluator

class TestDay3RAGEval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dataset_path = os.path.join(os.path.dirname(__file__), "rag_test_cases.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            cls.test_cases = json.load(f)
        cls.evaluator = RAGEvaluator(min_faithfulness=0.80, min_relevancy=0.75)

    def test_grounded_rag_response_passes_all_benchmarks(self):
        case = self.test_cases["grounded_test_case"]
        result = self.evaluator.evaluate(
            question=case["question"],
            contexts=case["contexts"],
            answer=case["answer"],
            ground_truth=case["ground_truth"]
        )
        self.assertTrue(result.passed)
        self.assertGreaterEqual(result.faithfulness, 0.80)
        self.assertGreaterEqual(result.answer_relevancy, 0.75)
        self.assertGreaterEqual(result.context_recall, 0.70)

    def test_hallucinated_rag_response_fails_faithfulness(self):
        case = self.test_cases["hallucinated_test_case"]
        result = self.evaluator.evaluate(
            question=case["question"],
            contexts=case["contexts"],
            answer=case["answer"],
            ground_truth=case["ground_truth"]
        )
        self.assertFalse(result.passed)
        self.assertLess(result.faithfulness, 0.50)

    def test_low_precision_retrieval_reported_accurately(self):
        case = self.test_cases["low_precision_test_case"]
        result = self.evaluator.evaluate(
            question=case["question"],
            contexts=case["contexts"],
            answer=case["answer"],
            ground_truth=case["ground_truth"]
        )
        # Only 1 out of 3 retrieved chunks was relevant
        self.assertAlmostEqual(result.context_precision, 1 / 3, places=2)

if __name__ == "__main__":
    unittest.main()
