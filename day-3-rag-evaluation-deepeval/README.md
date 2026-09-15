# Day 3: Retrieval-Augmented Generation (RAG) Evaluation

## Lab Overview
In this module, you implement and audit core RAG quality metrics following the **DeepEval** and **Ragas** patterns: Faithfulness, Answer Relevancy, Context Precision, and Context Recall.

### Key Metrics
- **Faithfulness**: Quantifies the percentage of claims in the generated response that can be directly attributed to the retrieved context chunks.
- **Answer Relevancy**: Assesses whether the model actually addressed the user's intent or drifted into tangential points.
- **Context Precision**: Measures whether relevant reference documentation was ranked at the top of the vector search context window.

## Running Tests
Run the standalone Day 3 test suite:
```bash
python3 -m unittest test_day3_rag_eval.py
```
