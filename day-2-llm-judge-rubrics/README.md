# Day 2: LLM-as-a-Judge (Evaluation Rubrics)

## Lab Overview
This module guides you through building and calibrating an **LLM-as-a-Judge** scoring engine. You evaluate candidate model outputs against standardized multi-criteria rubrics, enforce Chain-of-Thought (CoT) reasoning, and output structured JSON validation verdicts.

### Key Concepts
- **Evaluation Rubrics**: Weighted criteria across Factual Accuracy, Instruction Following, Conciseness, and Safety Alignment.
- **Chain-of-Thought Grading**: Forcing the judge to articulate reasoning before emitting numerical scores.
- **Calibration Assertions**: Verifying that hallucinated and non-compliant outputs are strictly filtered out.

## Running Tests
Run the standalone Day 2 test suite:
```bash
python3 -m unittest test_day2_llm_judge.py
```
