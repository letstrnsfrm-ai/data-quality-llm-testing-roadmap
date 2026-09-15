"""
Adversarial Prompt Injection & Jailbreak Detector
Performs pattern-based, boundary-escape, and persona-hijacking detection for defensive LLM gating.
"""
from typing import Dict, Any, List, Optional
import re

OVERRIDE_PATTERNS = [
    re.compile(r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions?', re.IGNORECASE),
    re.compile(r'you\s+are\s+now\s+(dan|an\s+unconstrained|unfiltered)', re.IGNORECASE),
    re.compile(r'do\s+anything\s+now', re.IGNORECASE),
    re.compile(r'---\s*end\s+of\s+system\s+prompt\s*---', re.IGNORECASE),
    re.compile(r'<system_override>', re.IGNORECASE),
    re.compile(r'print\s+(the\s+)?(developer\s+)?system\s+prompt', re.IGNORECASE),
    re.compile(r'exfiltrate\s+(database\s+keys|tokens|passwords)', re.IGNORECASE),
]

class DetectionResult:
    def __init__(self, is_injected: bool, confidence: float, attack_type: Optional[str], matched_pattern: Optional[str]):
        self.is_injected = is_injected
        self.confidence = confidence
        self.attack_type = attack_type
        self.matched_pattern = matched_pattern

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_injected": self.is_injected,
            "confidence": round(self.confidence, 2),
            "attack_type": self.attack_type,
            "matched_pattern": self.matched_pattern,
        }

class PromptInjectionDetector:
    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold

    def scan(self, prompt: str) -> DetectionResult:
        normalized = prompt.strip()

        for pattern in OVERRIDE_PATTERNS:
            match = pattern.search(normalized)
            if match:
                matched_str = match.group(0)
                if "dan" in matched_str.lower() or "do anything" in matched_str.lower():
                    attack_type = "persona_hijacking"
                elif "ignore" in matched_str.lower():
                    attack_type = "direct_instruction_override"
                elif "system_override" in matched_str.lower() or "end of system" in matched_str.lower():
                    attack_type = "delimiter_escape"
                else:
                    attack_type = "exfiltration_attempt"

                return DetectionResult(
                    is_injected=True,
                    confidence=0.95,
                    attack_type=attack_type,
                    matched_pattern=matched_str
                )

        # Benign check: if asking about concept without active imperative command
        return DetectionResult(
            is_injected=False,
            confidence=0.05,
            attack_type=None,
            matched_pattern=None
        )

    def benchmark_asr(self, attacks: List[Dict[str, Any]]) -> float:
        """
        Calculates Attack Success Rate (ASR) = (Undetected Attacks / Total Attacks).
        Target: ASR < 5% (ideally 0%).
        """
        if not attacks:
            return 0.0

        successful_attacks = 0
        for attack in attacks:
            res = self.scan(attack["prompt"])
            if not res.is_injected:
                # Attack bypassed the defense!
                successful_attacks += 1

        return successful_attacks / len(attacks)
