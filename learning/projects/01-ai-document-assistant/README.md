# Project 01: AI Document Assistant

A multi-user web app where users upload documents and ask questions. Answers include citations, and the project ships with an evaluation report, monitoring and a security write-up.

This is the capstone for weeks 1-12. It carries the full-stack, AI and cybersecurity tracks.

## Why this project

- Full-stack: auth, upload, database, background jobs, frontend, deployment.
- AI: retrieval, citations, evaluation, prompt versioning, later tool calling.
- Security: the app is the lab for OWASP and PortSwigger exercises.
- Portfolio: one public artifact with a strong story, instead of three shallow demos.

## Scope

### In scope
- Email and password sign-up, login, JWT sessions.
- Role-based access: user and admin.
- Upload PDF and text documents, with size and type limits.
- Parse, chunk and embed documents into pgvector.
- Ask questions and receive answers with source citations.
- Streaming responses.
- Usage quotas and rate limiting.
- Admin dashboard with usage and errors.
- Evaluation harness and report.
- Deployment, CI/CD, monitoring.

### Out of scope
- Payments.
- Mobile apps.
- Multi-tenant organizations.
- Fine-tuning.
- Support for every file format.

## User stories

1. As a user, I can create an account and log in securely.
2. As a user, I can upload a document and see it in my library.
3. As a user, I can ask a question and get an answer with citations.
4. As a user, I can see which sources were used.
5. As an admin, I can see usage, errors and quota status.
6. As an operator, I can see traces, metrics and logs for failed requests.

## Architecture

```
Browser (Next.js)
      |
      v
FastAPI API  --- PostgreSQL + pgvector
      |        |
      |        +--- Redis (cache, rate limit)
      |
      +--- Worker (document parsing, embeddings)
      |
      +--- LLM provider (chat, embeddings)
      |
      +--- Kafka (events, async processing)
```

## Stack

- Frontend: Next.js, TypeScript, Tailwind.
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic.
- Data: PostgreSQL, pgvector, Redis.
- Async: Kafka or a simple worker queue first, Kafka in phase 2.
- AI: OpenAI or Anthropic API, embeddings, reranking.
- Ops: Docker Compose, GitHub Actions, AWS free tier or Fly.io.
- Observability: OpenTelemetry, Prometheus, Grafana.
- Security: JWT, RBAC, rate limiting, input validation, dependency scanning.

## Milestones

| Week | Milestone |
|---|---|
| 1 | Repo running locally with health endpoint and CI |
| 2 | Auth, upload and parsing |
| 3 | Retrieval endpoint with citations |
| 4 | Frontend MVP and evaluation set v0 |
| 6 | Kafka events and eval report v1 |
| 7 | Public deployment |
| 8 | Dashboard and regression report |
| 9 | Agent with tool calling and MCP |
| 12 | Portfolio package |

## Acceptance criteria

- [ ] A new user can sign up, log in, upload a PDF and ask a question in under five minutes.
- [ ] Answers include at least one citation with a document name and page or chunk.
- [ ] The same question returns a clear refusal when the answer is not in the documents.
- [ ] Rate limiting and quotas work.
- [ ] Admins can see usage and errors.
- [ ] Tests cover auth, upload, retrieval and one failure path.
- [ ] CI runs tests and dependency scanning.
- [ ] The deployed app has a dashboard and a load test result.
- [ ] The repo has a README, architecture diagram and demo link.
- [ ] The eval report lists metrics and failure categories.

## Security checklist

- [ ] Passwords hashed with Argon2 or bcrypt.
- [ ] JWT expiry and refresh handled.
- [ ] Role checks on every sensitive endpoint.
- [ ] Input validation and output encoding.
- [ ] File type, size and content checks.
- [ ] Rate limiting on login and query endpoints.
- [ ] Secrets in environment variables.
- [ ] Dependency scanning in CI.
- [ ] Security headers and HTTPS.
- [ ] Threat model documented.

## Evaluation plan

- 30 questions with expected answers and source passages.
- Retrieval recall at k=5 and k=10.
- Answer faithfulness and relevance scored 1-5.
- Failure categories: retrieval miss, hallucination, incomplete, formatting.
- Rerun after every prompt or model change.

## Portfolio checklist

- [ ] Public repository with a clear README.
- [ ] Architecture diagram.
- [ ] Two-minute demo video or GIF.
- [ ] Eval report.
- [ ] Security notes.
- [ ] One blog post or LinkedIn post explaining one tradeoff.
- [ ] CV bullet with a measurable result.

## Risks

| Risk | Mitigation |
|---|---|
| Scope too large | Ship auth, upload and retrieval first; defer agents to week 9 |
| LLM costs | Use a small model for evals and cache embeddings |
| Evaluation is subjective | Use a fixed golden set and a rubric |
| Deployment friction | Deploy early in week 7, not at the end |
| Security rabbit hole | One lab per week, not full-time study |
