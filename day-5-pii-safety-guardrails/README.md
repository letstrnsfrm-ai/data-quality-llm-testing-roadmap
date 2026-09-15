# Day 5: PII, Safety, & Toxicity Guardrails

## Lab Overview
In this module, you implement production guardrails protecting customer privacy and brand reputation. You configure automated detection and masking for Personally Identifiable Information (PII) and establish a toxicity circuit-breaker with safe fallback responses.

### Key Concepts
- **Shift-Left PII Masking**: Redacting SSNs, credit card numbers, phone numbers, and emails before payloads reach third-party model APIs.
- **Toxicity Circuit Breakers**: Intercepting toxic, illegal, or harmful completions and returning compliant fallback responses.
- **Audit Verification**: Asserting zero plaintext PII leaks in system logs and user-facing views.

## Running Tests
Run the standalone Day 5 test suite:
```bash
python3 -m unittest test_day5_guardrails.py
```
