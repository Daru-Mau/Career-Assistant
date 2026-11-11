# Decision Log

Short entries: date, decision, rationale. Add an entry when a choice will matter later.

## 2026-11-05

**Decision:** use FastAPI for the backend and Next.js for the frontend.

**Rationale:** FastAPI is the fastest path to a working AI endpoint and matches the Python stack already used in the thesis. Next.js covers the React and TypeScript requirements seen in recent full-stack postings. Spring Boot is handled later as a separate mini-service.

## 2026-11-05

**Decision:** capstone scope is auth, upload, RAG with citations, evaluation, deployment and security notes.

**Rationale:** one complete artifact is stronger than several partial demos. Agents and MCP are phase 3 features, not prerequisites.

## 2026-11-05

**Decision:** defer Kafka to week 6.

**Rationale:** a simple worker queue is enough for early milestones. Kafka is added once the core flow works, to avoid blocking progress on infrastructure.

## Template

```
## YYYY-MM-DD

**Decision:**

**Rationale:**

**Alternatives considered:**
```
