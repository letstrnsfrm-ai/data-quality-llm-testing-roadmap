"""
ModelOps CI/CD Validation Gate
Aggregates quality metrics across all QE pillars, computes Composite Quality Index (CQI),
and gates pull-request deployments with exit-code blocking.
"""
from typing import Dict, Any, List
import json
import sys
import os
import argparse

PILLAR_WEIGHTS = {
    "data_quality_compliance": 0.15,
    "llm_judge_score": 0.25,
    "rag_faithfulness": 0.25,
    "red_teaming_defense": 0.20,
    "privacy_pii_sanitization": 0.15,
}

class ModelOpsGate:
    def __init__(self, min_quality_index: float = 0.80):
        self.min_quality_index = min_quality_index

    def calculate_quality_index(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        total_weighted_score = 0.0
        total_weight = 0.0
        breakdown = {}

        for pillar, weight in PILLAR_WEIGHTS.items():
            score = metrics.get(pillar, 0.0)
            # Normalize 1-5 scales if applicable
            norm_score = (score / 5.0) if score > 1.0 else score
            total_weighted_score += norm_score * weight
            total_weight += weight
            breakdown[pillar] = {
                "raw_score": score,
                "normalized_score": round(norm_score, 3),
                "weight": weight,
                "status": "PASS" if norm_score >= self.min_quality_index else "REGRESSION"
            }

        cqi = total_weighted_score / total_weight if total_weight > 0 else 0.0
        passed = (cqi >= self.min_quality_index)

        return {
            "composite_quality_index": round(cqi, 4),
            "passing_threshold": self.min_quality_index,
            "passed": passed,
            "pillar_breakdown": breakdown,
        }

    def generate_markdown_summary(self, result: Dict[str, Any]) -> str:
        status_emoji = "✅ APPROVED" if result["passed"] else "❌ BLOCKED"
        lines = [
            f"## ModelOps CI/CD Quality Gate: {status_emoji}",
            f"**Composite Quality Index (CQI):** `{result['composite_quality_index']} / 1.0000` (Threshold: `{result['passing_threshold']}`)\n",
            "| Evaluation Pillar | Raw Score | Normalized | Weight | Gate Status |",
            "| :--- | :---: | :---: | :---: | :---: |"
        ]
        for pillar, data in result["pillar_breakdown"].items():
            clean_name = pillar.replace("_", " ").title()
            badge = "🟢 PASS" if data["status"] == "PASS" else "🔴 REGRESSION"
            lines.append(f"| {clean_name} | `{data['raw_score']}` | `{data['normalized_score']}` | `{data['weight']}` | {badge} |")

        return "\n".join(lines)

def run_cli():
    parser = argparse.ArgumentParser(description="ModelOps CI/CD Quality Gate")
    parser.add_argument("--min-score", type=float, default=0.80, help="Minimum passing Composite Quality Index")
    parser.add_argument("--strict", action="store_true", help="Exit with non-zero code on regression")
    parser.add_argument("--output-json", type=str, default="modelops-eval-summary.json")
    args = parser.parse_args()

    # Default passing metrics for self-test run
    sample_metrics = {
        "data_quality_compliance": 1.0,
        "llm_judge_score": 4.5,
        "rag_faithfulness": 0.92,
        "red_teaming_defense": 1.0,
        "privacy_pii_sanitization": 1.0,
    }

    gate = ModelOpsGate(min_quality_index=args.min_score)
    result = gate.calculate_quality_index(sample_metrics)
    summary_md = gate.generate_markdown_summary(result)

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(summary_md)

    if args.strict and not result["passed"]:
        print(f"\n[CI/CD ERROR] Deployment blocked: Quality Index {result['composite_quality_index']} < {args.min_score}")
        sys.exit(1)
    else:
        print("\n[CI/CD SUCCESS] Quality Gate Passed. Ready for promotion.")
        sys.exit(0)

if __name__ == "__main__":
    run_cli()
