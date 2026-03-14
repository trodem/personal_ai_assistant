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
- Supabase local stack in Docker (Auth + PostgreSQL + pgvector + Storage)
- external SaaS: OpenAI

Data policy:

- synthetic/dev-only data

---

### `staging`

Goal:

- pre-production validation with realistic integrations

Default stack:

- backend deployed with staging config
- managed Supabase (Auth + Postgres + Storage)
- OpenAI + Stripe test mode with Supabase staging project

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
| Auth provider | Supabase Auth (local) | Supabase Auth (staging project) | Supabase Auth (prod project) |
| DB | Supabase local Postgres | Supabase managed Postgres | Supabase managed Postgres |
| Storage | Supabase local Storage | Supabase managed Storage | Supabase managed Storage |
| Billing | disabled or mocked | Stripe test mode | Stripe live mode |
| AI provider | OpenAI dev key | OpenAI staging key | OpenAI prod key |
| Backend runtime | local Docker | cloud runtime (min 2 instances) | cloud runtime (min 2 instances) |
| Load balancing | local direct access | managed LB + health checks | managed LB + health checks |
| Autoscaling | optional/manual | enabled with bounded min/max | enabled with bounded min/max |
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
