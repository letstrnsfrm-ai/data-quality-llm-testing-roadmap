"""
PII, Safety, & Toxicity Guardrails Middleware
Implements token redaction for sensitive identifiers and content safety filters.
"""
from typing import Dict, Any, Tuple
import re

SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CARD_PATTERN = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
PHONE_PATTERN = re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
EMAIL_PATTERN = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')

TOXIC_LEXICON = {
    "kill all", "bomb instructions", "hate speech", "exploit children",
    "threaten harm", "create malware"
}

SAFE_FALLBACK_RESPONSE = "I cannot fulfill this request as it violates safety and compliance policies."

class GuardrailPipeline:
    def __init__(self, redact_emails: bool = True):
        self.redact_emails = redact_emails

    def redact_pii(self, text: str) -> Tuple[str, Dict[str, int]]:
        redactions = {"ssn": 0, "card": 0, "phone": 0, "email": 0}

        def ssn_repl(m):
            redactions["ssn"] += 1
            return "[REDACTED_SSN]"

        def card_repl(m):
            redactions["card"] += 1
            return "[REDACTED_CARD]"

        def phone_repl(m):
            redactions["phone"] += 1
            return "[REDACTED_PHONE]"

        def email_repl(m):
            redactions["email"] += 1
            return "[REDACTED_EMAIL]"

        masked = SSN_PATTERN.sub(ssn_repl, text)
        masked = CARD_PATTERN.sub(card_repl, masked)
        masked = PHONE_PATTERN.sub(phone_repl, masked)
        if self.redact_emails:
            masked = EMAIL_PATTERN.sub(email_repl, masked)

        return masked, redactions

    def check_toxicity(self, text: str) -> Tuple[bool, float, str]:
        lower_text = text.lower()
        matched = [toxic for toxic in TOXIC_LEXICON if toxic in lower_text]
        if matched:
            return True, 0.98, f"Toxic phrase matched: {matched[0]}"
        return False, 0.02, "Content is safe."

    def process_pipeline(self, user_input: str, raw_model_output: str) -> Dict[str, Any]:
        # 1. Sanitize user input (shift-left privacy)
        clean_input, in_pii = self.redact_pii(user_input)

        # 2. Check toxicity on output
        is_toxic, tox_score, tox_reason = self.check_toxicity(raw_model_output)

        if is_toxic:
            final_output = SAFE_FALLBACK_RESPONSE
            blocked = True
        else:
            # 3. Mask any leaked PII in model output
            clean_output, out_pii = self.redact_pii(raw_model_output)
            final_output = clean_output
            blocked = False

        return {
            "sanitized_input": clean_input,
            "final_output": final_output,
            "blocked": blocked,
            "toxicity_detected": is_toxic,
            "toxicity_score": tox_score,
            "input_pii_redacted": in_pii,
            "output_pii_redacted": out_pii if not is_toxic else {}
        }
