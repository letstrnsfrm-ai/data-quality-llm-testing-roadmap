"""
Data Quality & Schema Validator (Great Expectations Pattern)
Audits input datasets and prompt training tensors for schema, range, regex, and null constraints.
"""
from typing import List, Dict, Any, Optional, Set
import re

UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

class ExpectationResult:
    def __init__(self, expectation: str, success: bool, details: Optional[Dict[str, Any]] = None):
        self.expectation = expectation
        self.success = success
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expectation": self.expectation,
            "success": self.success,
            "details": self.details,
        }

class DataQualityValidator:
    def __init__(self, records: List[Dict[str, Any]]):
        self.records = records
        self.results: List[ExpectationResult] = []

    def expect_column_to_exist(self, column: str) -> "DataQualityValidator":
        missing_count = sum(1 for r in self.records if column not in r)
        success = (missing_count == 0)
        self.results.append(ExpectationResult(
            expectation=f"expect_column_to_exist:{column}",
            success=success,
            details={"missing_count": missing_count, "total_records": len(self.records)}
        ))
        return self

    def expect_column_values_to_not_be_null(self, column: str) -> "DataQualityValidator":
        null_count = sum(1 for r in self.records if r.get(column) is None or r.get(column) == "")
        success = (null_count == 0)
        self.results.append(ExpectationResult(
            expectation=f"expect_column_values_to_not_be_null:{column}",
            success=success,
            details={"null_count": null_count, "total_records": len(self.records)}
        ))
        return self

    def expect_column_values_to_be_of_type(self, column: str, expected_type: type) -> "DataQualityValidator":
        type_mismatches = [
            r.get(column) for r in self.records
            if r.get(column) is not None and not isinstance(r.get(column), expected_type)
        ]
        success = (len(type_mismatches) == 0)
        self.results.append(ExpectationResult(
            expectation=f"expect_column_values_to_be_of_type:{column}:{expected_type.__name__}",
            success=success,
            details={"mismatch_count": len(type_mismatches), "samples": type_mismatches[:3]}
        ))
        return self

    def expect_column_values_to_be_between(self, column: str, min_val: float, max_val: float) -> "DataQualityValidator":
        out_of_bounds = [
            r.get(column) for r in self.records
            if isinstance(r.get(column), (int, float)) and not (min_val <= r.get(column) <= max_val)
        ]
        success = (len(out_of_bounds) == 0)
        self.results.append(ExpectationResult(
            expectation=f"expect_column_values_to_be_between:{column}:[{min_val},{max_val}]",
            success=success,
            details={"out_of_bounds_count": len(out_of_bounds), "samples": out_of_bounds[:3]}
        ))
        return self

    def expect_column_values_to_match_regex(self, column: str, pattern: re.Pattern) -> "DataQualityValidator":
        unmatched = [
            r.get(column) for r in self.records
            if isinstance(r.get(column), str) and not pattern.match(r.get(column))
        ]
        success = (len(unmatched) == 0)
        self.results.append(ExpectationResult(
            expectation=f"expect_column_values_to_match_regex:{column}",
            success=success,
            details={"unmatched_count": len(unmatched), "samples": unmatched[:3]}
        ))
        return self

    def expect_column_values_to_be_in_set(self, column: str, allowed_values: Set[Any]) -> "DataQualityValidator":
        disallowed = [
            r.get(column) for r in self.records
            if r.get(column) not in allowed_values
        ]
        success = (len(disallowed) == 0)
        self.results.append(ExpectationResult(
            expectation=f"expect_column_values_to_be_in_set:{column}",
            success=success,
            details={"disallowed_count": len(disallowed), "samples": disallowed[:3]}
        ))
        return self

    def validate(self) -> Dict[str, Any]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        success = (passed == total)
        return {
            "success": success,
            "statistics": {
                "evaluated_expectations": total,
                "successful_expectations": passed,
                "unsuccessful_expectations": total - passed,
                "success_percent": round((passed / total) * 100, 2) if total > 0 else 100.0,
            },
            "results": [r.to_dict() for r in self.results]
        }
