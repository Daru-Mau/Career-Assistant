# Full-Stack Track

Budget: 4 hours per week
Goal: close the recurring production-backend gaps (Spring, Kafka, AWS, observability) while shipping the capstone.

## Skills checklist

### Backend
- [ ] FastAPI project structure with routers, services and schemas
- [ ] Pydantic validation and error contracts
- [ ] SQLAlchemy models, relationships and migrations with Alembic
- [ ] PostgreSQL schema design and indexing
- [ ] JWT authentication and role-based access control
- [ ] File upload, parsing and size limits
- [ ] Background jobs and task queues
- [ ] Redis caching and rate limiting
- [ ] Kafka producer and consumer basics
- [ ] Structured logging and correlation IDs
- [ ] pytest unit and integration tests

### Frontend
- [ ] Next.js App Router and layouts
- [ ] TypeScript types for API contracts
- [ ] Auth flow and protected routes
- [ ] Upload and chat interfaces
- [ ] Streaming responses and loading states
- [ ] Error handling and empty states
- [ ] Basic accessibility and mobile layout

### DevOps and operations
- [ ] Docker Compose for app, database, Redis
- [ ] GitHub Actions: lint, test, build
- [ ] Deploy to AWS free tier or Fly.io
- [ ] Environment and secrets management
- [ ] OpenTelemetry traces and metrics
- [ ] Prometheus and Grafana dashboard
- [ ] Load test with k6
- [ ] Runbook for common failures

### Enterprise backend (optional)
- [ ] Spring Boot project with REST controllers
- [ ] JPA entities and repositories
- [ ] Spring Security basics
- [ ] JUnit and MockMvc tests
- [ ] Dockerfile and CI pipeline

## Capstone tasks by week

| Week | Task |
|---|---|
| 1 | Repo, Compose, FastAPI skeleton, PostgreSQL, health endpoint, CI |
| 2 | Auth, users, RBAC, upload, parsing, tests |
| 3 | Document CRUD, background processing, error handling |
| 4 | Next.js login, upload and chat UI |
| 5 | Redis cache, rate limits, quotas |
| 6 | Kafka event pipeline |
| 7 | Deploy, CI/CD, load test |
| 8 | OpenTelemetry, Prometheus, Grafana |
| 9 | Admin dashboard and audit log |
| 10 | UI polish, accessibility, mobile |
| 11 | Optional Spring Boot service |
| 12 | README, architecture, demo |

## Optional Spring Boot mini-service

Scope: a small service with one domain, for example a document metadata API.

- REST controller, service, repository.
- PostgreSQL with JPA.
- Spring Security with JWT or basic auth.
- JUnit and MockMvc tests.
- Dockerfile and GitHub Actions.

Done when it runs with one command, has tests and a short README.

## Done criteria

- Capstone runs locally with one command.
- Tests cover auth, upload, retrieval and at least one failure path.
- CI runs on every push.
- The deployed app has a dashboard and a load test result.
- README explains architecture, tradeoffs and how to run it.

## Resources

See `../resources.md`. Prioritize FastAPI docs, PostgreSQL Tutorial, Docker docs, GitHub Actions docs and DDIA.
