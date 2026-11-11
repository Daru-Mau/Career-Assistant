# Project 02: Spring Boot Mini-Service (optional)

A small, complete service built to close the recurring Spring and Java gap seen in backend applications (Cisco, Banca Mediolanum). Run it only if the capstone is on track or after week 12.

## Scope

Build a document metadata API.

- Create, read, update and delete document metadata.
- PostgreSQL persistence with JPA.
- Validation and error responses.
- Authentication with JWT or basic auth.
- Tests with JUnit and MockMvc.
- Dockerfile and GitHub Actions.
- Short README with architecture and run instructions.

## Stack

- Java 21, Spring Boot 3.
- Spring Web, Spring Data JPA, Spring Security.
- PostgreSQL.
- JUnit 5, MockMvc.
- Docker, GitHub Actions.

## Milestones

| Session | Task |
|---|---|
| 1 | Project skeleton, one entity, one repository, one controller |
| 2 | CRUD endpoints and validation |
| 3 | PostgreSQL, migrations, integration tests |
| 4 | Security and auth |
| 5 | Dockerfile, CI, README |

## Acceptance criteria

- [ ] Runs with one command.
- [ ] CRUD endpoints work and return consistent errors.
- [ ] Tests cover the happy path and one failure path.
- [ ] Auth protects write endpoints.
- [ ] CI runs tests.
- [ ] README explains the design and how to run it.

## Why it matters

Spring appears in enterprise backend postings and in the Banca Mediolanum fit assessment. A small working service is enough to speak credibly about controllers, JPA, security and testing without claiming production experience.

## Resources

See `../../resources.md`. Prioritize Spring Academy and the official Spring Boot guides.
