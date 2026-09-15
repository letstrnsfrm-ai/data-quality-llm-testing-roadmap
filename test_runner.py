#!/usr/bin/env python3
"""
Unified Test Runner for Data Quality & AI/LLM Testing Reference Suite (Days 1–7).
Runs all lab test suites, benchmarks pass rates, and renders an empirical summary table.
"""
import unittest
import time
import sys
import os

LABS = [
    ("Day 1", "Data Quality & Schema Auditing", "day-1-data-quality-schema-auditing/test_day1_data_quality.py"),
    ("Day 2", "LLM-as-a-Judge Evaluation Rubrics", "day-2-llm-judge-rubrics/test_day2_llm_judge.py"),
    ("Day 3", "RAG Retrieval & Faithfulness Metrics", "day-3-rag-evaluation-deepeval/test_day3_rag_eval.py"),
    ("Day 4", "Adversarial Red-Teaming & Prompt Injection", "day-4-red-teaming-prompt-injection/test_day4_red_teaming.py"),
    ("Day 5", "PII, Safety & Toxicity Guardrails", "day-5-pii-safety-guardrails/test_day5_guardrails.py"),
    ("Day 6", "Vector Database & Embedding Recall", "day-6-vectordb-embedding-audits/test_day6_vectordb.py"),
    ("Day 7", "ModelOps CI/CD Validation Gates", "day-7-modelops-cicd-gates/test_day7_modelops_gate.py"),
]

def run_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results = []
    total_tests = 0
    total_failures = 0
    total_errors = 0
    start_total = time.time()

    print("\n" + "=" * 80)
    print("🚀 Running AI/LLM Testing 7-Day Empirical Test Suite")
    print("=" * 80 + "\n")

    for day_label, title, test_rel_path in LABS:
        test_file = os.path.join(base_dir, test_rel_path)
        test_dir = os.path.dirname(test_file)
        test_module_name = os.path.splitext(os.path.basename(test_file))[0]

        # Add directory to sys.path so modules inside can import their siblings
        if test_dir not in sys.path:
            sys.path.insert(0, test_dir)

        loader = unittest.TestLoader()
        start_time = time.time()
        suite = loader.discover(start_dir=test_dir, pattern=os.path.basename(test_file))
        
        runner = unittest.TextTestRunner(verbosity=0)
        res = runner.run(suite)
        elapsed = time.time() - start_time

        num_tests = res.testsRun
        failures = len(res.failures)
        errors = len(res.errors)
        passed = (failures == 0 and errors == 0)

        total_tests += num_tests
        total_failures += failures
        total_errors += errors

        results.append({
            "day": day_label,
            "title": title,
            "tests": num_tests,
            "passed": passed,
            "elapsed": elapsed
        })

    total_time = time.time() - start_total

    print("\n" + "-" * 80)
    print(f"{'Day':<8} | {'Track Module':<42} | {'Tests':<6} | {'Status':<10} | {'Duration'}")
    print("-" * 80)
    for r in results:
        status_str = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"{r['day']:<8} | {r['title']:<42} | {r['tests']:<6} | {status_str:<10} | {r['elapsed']*1000:.1f}ms")
    print("-" * 80)
    print(f"Total Tests Executed : {total_tests}")
    print(f"Total Failures/Errors: {total_failures + total_errors}")
    print(f"Success Rate         : {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
    print(f"Total Elapsed Time   : {total_time:.3f}s")
    print("=" * 80 + "\n")

    if total_failures > 0 or total_errors > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_all()
