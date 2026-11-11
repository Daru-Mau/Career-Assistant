# 12-Week Learning Plan

Start: 2026-11-05 (week 45)
Budget: 12 hours per week
Primary focus: developer, full-stack and AI
Secondary: cybersecurity coverage and Italian

## Design principle

One capstone carries full-stack, AI and security. The tracks are layers of the same artifact, not separate courses. Italian and DSA run in parallel because they compound slowly and cannot be crammed.

## Weekly budget

| Track | Hours | Main output |
|---|---|---|
| Full-stack | 4 | Capstone backend, frontend, tests, deploy |
| AI | 3 | RAG, evals, agent features |
| Italian | 3 | Daily practice, weekly writing, tutor session |
| Cybersecurity | 1 | One lab per week, applied to the capstone |
| DSA and interview prep | 1 | 5 problems, 1 system design topic |
| **Total** | **12** | |

## Twelve-week roadmap

### Phase 1: Foundation (weeks 1-4)

| Week | Full-stack | AI | Cybersecurity | Italian | Output |
|---|---|---|---|---|---|
| 1 | Repo, Docker Compose, FastAPI skeleton, PostgreSQL, health endpoint, CI | LLM API smoke test, streaming prototype | OWASP Top 10 overview, threat model v0 | Placement check, daily routine starts | Repo running locally |
| 2 | Auth with JWT, users, RBAC, file upload, document parsing, tests | Embeddings, chunking, pgvector setup | Authentication and access control labs | Grammar review, first tutor session | Authenticated upload flow |
| 3 | CRUD for documents, background jobs, error handling | Retrieval endpoint, citations, streaming answers | SQL injection and XSS labs | Technical vocabulary, first written summary | RAG endpoint working |
| 4 | Next.js UI: login, upload, chat, citations | Prompt versioning, basic evaluation set | CSRF and SSRF labs, security headers | B2 mock reading and listening | Local MVP with auth and RAG |

### Phase 2: Production (weeks 5-8)

| Week | Full-stack | AI | Cybersecurity | Italian | Output |
|---|---|---|---|---|---|
| 5 | Redis cache, rate limiting, usage quotas | Retrieval quality: top-k, reranking | Business logic and IDOR labs | Speaking practice, second tutor session | Faster, safer API |
| 6 | Kafka event pipeline, async processing | Eval harness: golden set, relevance and faithfulness | Secure coding pass on capstone | Writing: technical summary | Eval report v1 |
| 7 | Deploy to AWS free tier or Fly.io, CI/CD, load test with k6 | Cost and latency tuning | Dependency scanning, secrets, SAST | B2 mock writing | Public deployment |
| 8 | OpenTelemetry, Prometheus, Grafana, structured logs | Regression run, prompt and model comparison | Lab review and security notes | B2 mock speaking, tutor feedback | Deployed app with dashboard |

### Phase 3: Portfolio and interviews (weeks 9-12)

| Week | Full-stack | AI | Cybersecurity | Italian | Output |
|---|---|---|---|---|---|
| 9 | Admin dashboard, audit log | Tool calling, MCP server, agent workflow | PortSwigger labs 9-10, Juice Shop | CILS/CELI B2 practice test | Agent feature |
| 10 | Polish UI, accessibility, mobile layout | Guardrails, fallback, observability for AI calls | Labs 11-12, threat model v1 | Writing: cover letter in Italian | Portfolio-ready app |
| 11 | Optional Spring Boot mini-service | Demo script and eval summary | Security checklist final | Mock interview in Italian | Mock interviews done |
| 12 | README, architecture diagram, demo video | Final eval report | Security write-up | CILS/CELI B2 mock exam | Portfolio package and 3-5 applications |

## Milestones

| Milestone | Week | Definition of done |
|---|---|---|
| M1: MVP | 4 | User can sign up, upload a document and ask a question with citations |
| M2: Production | 8 | App is deployed, monitored, load-tested and has an eval report |
| M3: Portfolio | 12 | Public repo, README, demo, security notes, updated CV, applications sent |

## Weekly schedule template

Adjust the days to your life. Protect the full-stack and AI blocks.

| Day | Time | Activity |
|---|---|---|
| Monday | 45 min | Full-stack project |
| Tuesday | 45 min | DSA problems |
| Wednesday | 45 min | Full-stack project |
| Thursday | 45 min | AI project |
| Friday | 45 min | AI project |
| Saturday | 2 h | Full-stack and AI integration |
| Sunday | 1 h | Cybersecurity lab |
| Daily | 25 min | Italian |
| Sunday | 20 min | Weekly review and log |

This adds up to roughly 12 hours when the daily Italian sessions are included.

## Success metrics at week 12

- One public capstone with auth, RAG, evals, deployment, monitoring and security notes.
- 60 DSA problems logged.
- 12 security labs completed and summarized.
- 5 STAR stories written.
- Italian at solid B2+, with a CILS or CELI B2 mock exam completed.
- CV and LinkedIn updated with the capstone and language progress.
- At least 3 targeted applications sent.

## Review cadence

- Weekly: fill `weekly-log.md`.
- Monthly: demo the current build, even if incomplete.
- Week 4, 8, 12: review progress, adjust the plan, update the CV.

## After week 12

Choose one of three directions:
1. Continue the capstone toward a real product and add users.
2. Start the Spring Boot service to target enterprise backend roles.
3. Deepen AI agents and evaluation for AI-native roles.

Do not start a new track before the capstone is public.
