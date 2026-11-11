# AI Track

Budget: 3 hours per week
Goal: move from AI coursework to a documented, evaluated LLM application.

## Skills checklist

### LLM fundamentals
- [ ] Chat completions, system prompts and structured outputs
- [ ] Streaming responses
- [ ] Token limits, cost and latency tradeoffs
- [ ] Prompt versioning and regression testing
- [ ] Guardrails and fallback behavior

### RAG
- [ ] Document parsing and chunking strategies
- [ ] Embeddings and vector search with pgvector
- [ ] Metadata filters and hybrid search
- [ ] Reranking
- [ ] Citations and answer grounding
- [ ] Handling missing context and refusal

### Evaluation
- [ ] Build a golden set of questions and expected answers
- [ ] Retrieval metrics: recall, precision, MRR
- [ ] Answer metrics: faithfulness, relevance, completeness
- [ ] Automated regression runs
- [ ] Human review of failures

### Agents
- [ ] Tool calling with schemas
- [ ] MCP server and client basics
- [ ] Multi-step workflow with state
- [ ] Error handling and retries
- [ ] Observability for model calls

## Capstone tasks by week

| Week | Task |
|---|---|
| 1 | LLM API smoke test, streaming prototype |
| 2 | Embeddings, chunking, pgvector schema |
| 3 | Retrieval endpoint, citations, streaming answers |
| 4 | Prompt versioning, first evaluation set |
| 5 | Top-k tuning and reranking |
| 6 | Eval harness and report v1 |
| 7 | Cost and latency tuning |
| 8 | Regression run and model comparison |
| 9 | Tool calling and MCP server |
| 10 | Guardrails and fallback |
| 11 | Demo script and eval summary |
| 12 | Final eval report |

## Evaluation plan

1. Create 30 questions from the sample documents, with expected answers and source passages.
2. Measure retrieval recall at k=5 and k=10.
3. Measure answer faithfulness and relevance on a 1-5 scale, with a second reviewer if possible.
4. Log failures by category: retrieval miss, hallucination, incomplete answer, formatting error.
5. Rerun after every prompt or model change and store the results.

## Done criteria

- A user can upload a document, ask a question and receive an answer with citations.
- The repo contains an evaluation report with metrics and failure analysis.
- The README explains chunking, retrieval, prompting and evaluation choices.
- The agent feature works on at least two tools and fails safely.

## Resources

See `../resources.md`. Prioritize OpenAI or Anthropic docs, DeepLearning.AI short courses, pgvector docs and Ragas.
