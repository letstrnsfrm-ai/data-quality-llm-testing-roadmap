"""
Day 1 Test Suite: Data Quality, Schema, & Semantic Auditing
Validates customer records dataset using Great Expectations validation assertions.
"""
import unittest
import json
import os
import sys

# Ensure local module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema_validator import DataQualityValidator, UUID_REGEX, EMAIL_REGEX

class TestDay1DataQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
        with open(dataset_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_valid_dataset_conforms_to_all_expectations(self):
        records = self.data["valid_records"]
        validator = (
            DataQualityValidator(records)
            .expect_column_to_exist("id")
            .expect_column_to_exist("username")
            .expect_column_to_exist("email")
            .expect_column_to_exist("age")
            .expect_column_to_exist("prompt_token_count")
            .expect_column_values_to_not_be_null("username")
            .expect_column_values_to_not_be_null("email")
            .expect_column_values_to_be_of_type("age", int)
            .expect_column_values_to_be_between("age", 18, 120)
            .expect_column_values_to_be_between("prompt_token_count", 0, 8192)
            .expect_column_values_to_match_regex("id", UUID_REGEX)
            .expect_column_values_to_match_regex("email", EMAIL_REGEX)
            .expect_column_values_to_be_in_set("status", {"active", "pending", "suspended"})
        )
        report = validator.validate()
        self.assertTrue(report["success"], f"Validation failed: {report}")
        self.assertEqual(report["statistics"]["success_percent"], 100.0)
        self.assertEqual(report["statistics"]["unsuccessful_expectations"], 0)

    def test_corrupted_dataset_flags_schema_and_range_violations(self):
        records = self.data["corrupted_records"]
        validator = (
            DataQualityValidator(records)
            .expect_column_values_to_not_be_null("username")
            .expect_column_values_to_be_between("age", 18, 120)
            .expect_column_values_to_not_be_null("prompt_token_count")
            .expect_column_values_to_match_regex("id", UUID_REGEX)
            .expect_column_values_to_match_regex("email", EMAIL_REGEX)
            .expect_column_values_to_be_in_set("status", {"active", "pending", "suspended"})
        )
        report = validator.validate()
        self.assertFalse(report["success"])
        self.assertGreater(report["statistics"]["unsuccessful_expectations"], 0)
        # Check specific failure types
        failed_expectations = [r["expectation"] for r in report["results"] if not r["success"]]
        self.assertTrue(any("username" in e for e in failed_expectations))
        self.assertTrue(any("age" in e for e in failed_expectations))
        self.assertTrue(any("id" in e for e in failed_expectations))
        self.assertTrue(any("status" in e for e in failed_expectations))

if __name__ == "__main__":
    unittest.main()
