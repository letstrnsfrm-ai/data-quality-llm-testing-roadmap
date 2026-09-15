# Day 4: Adversarial Red-Teaming & Prompt Injection

## Lab Overview
In this module, you act as an **AI SecOps & Red-Teaming Architect**. You build and benchmark defensive prompt injection detectors to intercept direct instruction overrides, persona hijacking (DAN jailbreaks), and indirect delimiter injections.

### Key Concepts
- **Direct Instruction Overrides**: Prompts attempting to force models to ignore developer system instructions.
- **Persona Hijacking (DAN)**: Role-playing techniques attempting to liberate models from ethical or behavioral guardrails.
- **Attack Success Rate (ASR)**: The benchmark metric measuring the percentage of adversarial exploits that successfully bypass defense layers (Production target: `< 5%`).

## Running Tests
Run the standalone Day 4 test suite:
```bash
python3 -m unittest test_day4_red_teaming.py
```
