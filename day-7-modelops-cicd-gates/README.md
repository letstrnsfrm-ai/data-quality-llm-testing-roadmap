# Day 7: ModelOps CI/CD Validation Gates

## Lab Overview
In this final capstone module, you synthesize all previous evaluation pillars into an automated CI/CD Quality Gate. You compute a Composite Quality Index (CQI), assert regression thresholds, and block faulty pull requests with non-zero exit codes.

### Key Concepts
- **Composite Quality Index (CQI)**: A single weighted score summarizing Data Quality, LLM Judge, RAG Grounding, Security Defenses, and Privacy.
- **Pull Request Blocking Gates**: Halting automated deployments if CQI drops below your organization's quality SLA (e.g. `< 0.80`).
- **SARIF & Markdown Summaries**: Generating actionable pipeline reports for engineering reviewers.

## Running Tests
Run the standalone Day 7 test suite:
```bash
python3 -m unittest test_day7_modelops_gate.py
```
Or execute the CLI evaluation gate in strict mode:
```bash
python3 eval_gate.py --strict --min-score 0.80
```
