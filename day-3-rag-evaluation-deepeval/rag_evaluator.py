"""
RAG Evaluation Metric Engine (DeepEval / Ragas Pattern)
Computes Faithfulness, Context Precision, Context Recall, and Answer Relevancy.
"""
from typing import List, Dict, Any, Optional
import re

def tokenize(text: str) -> set:
    return set(w for w in re.findall(r'\b[a-z0-9_]+\b', text.lower()) if len(w) > 2)

class RAGEvaluationResult:
    def __init__(
        self,
        faithfulness: float,
        answer_relevancy: float,
        context_precision: float,
        context_recall: float,
        passed: bool,
        details: Dict[str, Any]
    ):
        self.faithfulness = faithfulness
        self.answer_relevancy = answer_relevancy
        self.context_precision = context_precision
        self.context_recall = context_recall
        self.passed = passed
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        return {
            "faithfulness": round(self.faithfulness, 3),
            "answer_relevancy": round(self.answer_relevancy, 3),
            "context_precision": round(self.context_precision, 3),
            "context_recall": round(self.context_recall, 3),
            "passed": self.passed,
            "details": self.details,
        }

class RAGEvaluator:
    def __init__(
        self,
        min_faithfulness: float = 0.80,
        min_relevancy: float = 0.75,
        min_precision: float = 0.50
    ):
        self.min_faithfulness = min_faithfulness
        self.min_relevancy = min_relevancy
        self.min_precision = min_precision

    def evaluate(
        self,
        question: str,
        contexts: List[str],
        answer: str,
        ground_truth: Optional[str] = None
    ) -> RAGEvaluationResult:
        combined_context = " ".join(contexts)
        context_tokens = tokenize(combined_context)
        answer_tokens = tokenize(answer)
        question_tokens = tokenize(question)

        # 1. Faithfulness: proportion of answer tokens/claims grounded in context
        grounded_tokens = answer_tokens.intersection(context_tokens)
        faithfulness = len(grounded_tokens) / len(answer_tokens) if answer_tokens else 1.0

        # Check for direct contradictions / hallucinations (numbers / key adjectives mismatch)
        # e.g., if context says "24-hour" and answer says "90 days"
        numbers_in_context = set(re.findall(r'\b\d+\b', combined_context))
        numbers_in_answer = set(re.findall(r'\b\d+\b', answer))
        if numbers_in_answer and not numbers_in_answer.issubset(numbers_in_context):
            faithfulness = min(faithfulness, 0.35)

        # 2. Answer Relevancy: alignment of answer with question intent
        q_overlap = answer_tokens.intersection(question_tokens)
        answer_relevancy = len(q_overlap) / len(question_tokens) if question_tokens else 1.0
        # Boost if answer contains question keywords + informational content
        answer_relevancy = min(1.0, answer_relevancy * 1.5)

        # 3. Context Precision: fraction of retrieved contexts that are actually relevant to question
        relevant_contexts = [c for c in contexts if len(tokenize(c).intersection(question_tokens)) >= 2]
        context_precision = len(relevant_contexts) / len(contexts) if contexts else 0.0

        # 4. Context Recall: fraction of ground truth facts present in contexts
        if ground_truth:
            gt_tokens = tokenize(ground_truth)
            gt_covered = gt_tokens.intersection(context_tokens)
            context_recall = len(gt_covered) / len(gt_tokens) if gt_tokens else 1.0
        else:
            context_recall = 1.0

        passed = (
            faithfulness >= self.min_faithfulness
            and answer_relevancy >= self.min_relevancy
        )

        return RAGEvaluationResult(
            faithfulness=faithfulness,
            answer_relevancy=answer_relevancy,
            context_precision=context_precision,
            context_recall=context_recall,
            passed=passed,
            details={
                "grounded_token_count": len(grounded_tokens),
                "total_answer_tokens": len(answer_tokens),
                "relevant_chunks": len(relevant_contexts),
                "total_chunks": len(contexts)
            }
        )
