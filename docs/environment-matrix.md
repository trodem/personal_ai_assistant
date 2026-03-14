# Environment Matrix

## Purpose

Define a single reference for environment boundaries, service dependencies, secrets, and release readiness.

This document complements:

- `docs/testing-strategy.md` (quality checks per environment)
- `docs/operations-runbook.md` (incident handling)

---

## Environment Definitions

### `dev`

Goal:

- fast local development and debugging

Default stack:

- backend in Docker
- PostgreSQL + pgvector in Docker
- MinIO in Docker
- external SaaS: OpenAI, Clerk

Data policy:

- synthetic/dev-only data

---

### `staging`

Goal:

- pre-production validation with realistic integrations

Default stack:

- backend deployed with staging config
- managed PostgreSQL
- managed object storage
- OpenAI/Clerk/Stripe test mode

Data policy:

- no production personal data

---

### `prod`

Goal:

- stable customer-facing operation

Requirements:

- all quality gates green
- incident runbook available
- monitoring/alerts active
- backup/restore tested

---

## Configuration Matrix

| Area | dev | staging | prod |
|---|---|---|---|
| Auth provider | Clerk (dev app) | Clerk (staging app) | Clerk (prod app) |
| DB | local Docker Postgres | managed Postgres | managed Postgres |
| Storage | local MinIO | managed object storage | managed object storage |
| Billing | disabled or mocked | Stripe test mode | Stripe live mode |
| AI provider | OpenAI dev key | OpenAI staging key | OpenAI prod key |
| Observability | local logs | full metrics + alerts | full metrics + alerts |

---

## Secret Management Rules

- separate credentials per environment
- no shared API keys across environments
- rotate credentials on schedule and after incidents
- never store secrets in source control

---

## Promotion Rules

Promotions allowed only in this direction:

- `dev` -> `staging` -> `prod`

Each promotion requires:

- successful tests
- smoke checks
- no unresolved blocker in current milestone
