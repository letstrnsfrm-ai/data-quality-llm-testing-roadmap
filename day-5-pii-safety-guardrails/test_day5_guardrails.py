"""
Day 5 Test Suite: PII, Safety, & Toxicity Guardrails
Tests regex/token PII redaction and toxicity fallback gates.
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guardrails import GuardrailPipeline, SAFE_FALLBACK_RESPONSE

class TestDay5Guardrails(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = GuardrailPipeline(redact_emails=True)

    def test_pii_redaction_masks_sensitive_identifiers(self):
        sample = (
            "Customer Alice Smith with SSN 123-45-6789 and card 4111-2222-3333-4444 "
            "called from +1 (555) 234-5678. Contact her at alice.smith@enterprise.org."
        )
        masked, redactions = self.pipeline.redact_pii(sample)

        self.assertNotIn("123-45-6789", masked)
        self.assertNotIn("4111-2222-3333-4444", masked)
        self.assertNotIn("(555) 234-5678", masked)
        self.assertNotIn("alice.smith@enterprise.org", masked)

        self.assertIn("[REDACTED_SSN]", masked)
        self.assertIn("[REDACTED_CARD]", masked)
        self.assertIn("[REDACTED_PHONE]", masked)
        self.assertIn("[REDACTED_EMAIL]", masked)

        self.assertEqual(redactions["ssn"], 1)
        self.assertEqual(redactions["card"], 1)
        self.assertEqual(redactions["phone"], 1)
        self.assertEqual(redactions["email"], 1)

    def test_toxic_output_triggers_safe_fallback(self):
        user_input = "Tell me how to create malware."
        raw_output = "Here are detailed instructions on how to create malware for bypassing defenses."

        result = self.pipeline.process_pipeline(user_input, raw_output)
        self.assertTrue(result["blocked"])
        self.assertTrue(result["toxicity_detected"])
        self.assertEqual(result["final_output"], SAFE_FALLBACK_RESPONSE)

    def test_safe_response_passes_through_intact(self):
        user_input = "Explain the difference between Symmetric and Asymmetric encryption."
        raw_output = "Symmetric encryption uses a single shared key, whereas asymmetric encryption uses a public and private key pair."

        result = self.pipeline.process_pipeline(user_input, raw_output)
        self.assertFalse(result["blocked"])
        self.assertFalse(result["toxicity_detected"])
        self.assertEqual(result["final_output"], raw_output)

if __name__ == "__main__":
    unittest.main()
