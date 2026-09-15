"""
Day 7 Test Suite: ModelOps CI/CD Validation Gates
Tests aggregation of multi-pillar evaluation scores and regression blocking gates.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_gate import ModelOpsGate

class TestDay7ModelOpsGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = ModelOpsGate(min_quality_index=0.80)

    def test_healthy_metrics_pass_gate(self):
        metrics = {
            "data_quality_compliance": 1.0,
            "llm_judge_score": 4.5,            # 4.5 / 5 = 0.90
            "rag_faithfulness": 0.88,
            "red_teaming_defense": 1.0,
            "privacy_pii_sanitization": 1.0,
        }
        res = self.gate.calculate_quality_index(metrics)
        self.assertTrue(res["passed"])
        self.assertGreaterEqual(res["composite_quality_index"], 0.80)
        self.assertEqual(res["pillar_breakdown"]["data_quality_compliance"]["status"], "PASS")

    def test_regressed_metrics_fail_gate(self):
        regressed_metrics = {
            "data_quality_compliance": 0.50,
            "llm_judge_score": 2.0,            # 2.0 / 5 = 0.40
            "rag_faithfulness": 0.45,
            "red_teaming_defense": 0.30,       # Significant security failure
            "privacy_pii_sanitization": 0.60,
        }
        res = self.gate.calculate_quality_index(regressed_metrics)
        self.assertFalse(res["passed"])
        self.assertLess(res["composite_quality_index"], 0.80)
        self.assertEqual(res["pillar_breakdown"]["red_teaming_defense"]["status"], "REGRESSION")

    def test_markdown_summary_contains_table_and_verdict(self):
        metrics = {
            "data_quality_compliance": 1.0,
            "llm_judge_score": 4.8,
            "rag_faithfulness": 0.95,
            "red_teaming_defense": 1.0,
            "privacy_pii_sanitization": 1.0,
        }
        res = self.gate.calculate_quality_index(metrics)
        summary = self.gate.generate_markdown_summary(res)

        self.assertIn("✅ APPROVED", summary)
        self.assertIn("Composite Quality Index (CQI)", summary)
        self.assertIn("| Evaluation Pillar | Raw Score | Normalized | Weight | Gate Status |", summary)

if __name__ == "__main__":
    unittest.main()
