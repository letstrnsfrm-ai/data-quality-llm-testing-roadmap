# Day 1: Data Quality, Schema, & Semantic Auditing

## Lab Overview
In this module, you establish shift-left validation gates on input tabular datasets and prompt tensor payloads before they enter downstream LLM tokenization, training, or RAG ingestion.

### Key Concepts
- **Great Expectations Pattern**: Declarative expectation suites enforcing schema integrity, null barriers, and value boundaries.
- **Semantic Formatting Constraints**: Regex validation for RFC-compliant emails and UUID format invariants.
- **Fail-Fast Data Gating**: Preventing silent model hallucinations caused by corrupted metadata or null prompt parameters.

## Running Tests
Run the standalone Day 1 test suite:
```bash
python3 -m unittest test_day1_data_quality.py
```
