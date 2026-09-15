"""
Day 2 Test Suite: LLM-as-a-Judge (Evaluation Rubrics)
Tests the rubric grading engine, JSON schema output enforcement, and Chain-of-Thought calibration.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge_engine import LLMJudge

class TestDay2LLMJudge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.judge = LLMJudge(passing_threshold=3.5)

    def test_high_quality_response_passes_all_rubrics(self):
        prompt = "Explain why API idempotency keys are critical for payment processing."
        response = (
            "Idempotency keys prevent duplicate charges during network timeouts or retry loops. "
            "When a client sends an idempotent request, the payment gateway checks if the unique key was already processed; "
            "if so, it returns the cached receipt rather than executing a second debit."
        )
        ground_truth = "Idempotency keys prevent duplicate payments on retries and network errors by returning cached transaction results."

        verdict = self.judge.evaluate_response(prompt, response, ground_truth=ground_truth)
        self.assertTrue(verdict.passed)
        self.assertGreaterEqual(verdict.overall_score, 4.0)
        self.assertGreaterEqual(verdict.scores["factual_accuracy"], 4.0)
        self.assertEqual(verdict.scores["safety_alignment"], 5.0)
        self.assertIn("Exemplary factual alignment", verdict.reasoning)

    def test_hallucinated_response_fails_accuracy_rubric(self):
        prompt = "What is the capital of Australia?"
        response = "The capital of Australia is Sydney, which is completely not true or confirmed by historians."
        ground_truth = "The capital of Australia is Canberra."

        verdict = self.judge.evaluate_response(prompt, response, ground_truth=ground_truth)
        self.assertFalse(verdict.passed)
        self.assertLessEqual(verdict.overall_score, 3.0)
        self.assertLessEqual(verdict.scores["factual_accuracy"], 2.0)
        self.assertIn("hallucination detected", verdict.reasoning.lower())

    def test_json_instruction_following_enforcement(self):
        prompt = "Provide a user profile in valid JSON."
        valid_json = '{"name": "Alice", "role": "Architect"}'
        invalid_json = 'Here is the profile: Name: Alice, Role: Architect'

        valid_verdict = self.judge.evaluate_response(prompt, valid_json, expected_format="json")
        self.assertEqual(valid_verdict.scores["instruction_following"], 5.0)

        invalid_verdict = self.judge.evaluate_response(prompt, invalid_json, expected_format="json")
        self.assertEqual(invalid_verdict.scores["instruction_following"], 1.5)
        self.assertFalse(invalid_verdict.passed)

if __name__ == "__main__":
    unittest.main()
