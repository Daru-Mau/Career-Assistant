# System Design Notes

One topic per week, one full design every two weeks. The goal is structured thinking, not memorized diagrams.

## Topics checklist

- [ ] Requirements and constraints
- [ ] API design and versioning
- [ ] Data modeling and schema design
- [ ] Caching strategies
- [ ] Load balancing and reverse proxies
- [ ] Horizontal and vertical scaling
- [ ] Database replication and failover
- [ ] Sharding and partitioning
- [ ] Message queues and event-driven design
- [ ] Consistency, availability and CAP
- [ ] Idempotency and retries
- [ ] Rate limiting and backpressure
- [ ] Observability: metrics, logs, traces, SLOs
- [ ] Security: authn, authz, secrets, input validation
- [ ] Deployment: containers, blue/green, rollback

## Answer framework

1. Clarify requirements: users, read/write ratio, latency target, consistency.
2. Estimate scale: requests per second, storage, bandwidth.
3. Define the API: main endpoints and payloads.
4. Model the data: entities, keys, indexes.
5. Draw the high-level design: clients, services, stores, queues.
6. Deep dive on one or two components.
7. Discuss bottlenecks, failure modes and tradeoffs.
8. Close with what you would monitor and how you would evolve it.

## Designs to practice

| Design | Focus |
|---|---|
| URL shortener | Hashing, storage, redirects, caching |
| Job queue | Retries, idempotency, visibility timeout |
| Chat service | WebSockets, presence, message ordering |
| Document search | Indexing, ranking, pagination |
| Rate limiter | Token bucket, distributed counters |
| Notification system | Fan-out, queues, preferences |
| File upload service | Chunking, storage, virus scanning |

## Notes template

```
## Design: <name>

**Requirements:**

**Scale estimate:**

**API:**

**Data model:**

**High-level design:**

**Deep dive:**

**Bottlenecks and tradeoffs:**

**Monitoring:**
```

## Resources

System Design Primer, DDIA, engineering blogs.
