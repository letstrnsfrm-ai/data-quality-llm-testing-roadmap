# Day 6: Vector Database & Embedding Validation

## Lab Overview
In this module, you audit the retrieval engine powering RAG systems. You benchmark document chunking strategies, inspect TF-IDF vector embeddings, evaluate cosine distance boundaries, and assert `Recall@K` standards against known reference queries.

### Key Concepts
- **Chunk Window & Overlap Trade-offs**: Preserving semantic context across sentence boundaries without ballooning token storage costs.
- **Cosine Similarity Invariants**: Verifying mathematical normalization bounds `[0.0, 1.0]` and correct rank-ordering.
- **Recall@K SLA Benchmark**: Measuring the probability that relevant source documentation appears in top-$k$ context windows.

## Running Tests
Run the standalone Day 6 test suite:
```bash
python3 -m unittest test_day6_vectordb.py
```
