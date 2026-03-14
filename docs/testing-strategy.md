# Testing Strategy

## Purpose

Define how testing is executed, what is mandatory before merge, and which test level applies to each change type.

This document complements:

- `docs/development-roadmap.md` (what to build)
- `docs/error-model.md` (how failures are represented)
- `TODO.md` (when tasks are done)

---

## Test Levels

### Unit tests

Scope:

- pure business logic
- validators
- mappers
- utility functions

Rule:

- every non-trivial function must have unit coverage

---

### Integration tests

Scope:

- API handlers + service + repository interaction
- auth middleware behavior
- DB migrations and schema constraints

Rule:

- required for any backend feature touching persistence or auth

---

### End-to-end tests

Scope:

- critical product flows from request input to final output

Mandatory MVP e2e flows:

1. voice memory -> extraction -> clarification (if needed) -> confirmation -> persistence
2. question -> intent -> DB query/aggregation -> response generation
3. auth token -> protected endpoint access control
4. attachment upload -> storage -> authorized retrieval

---

## Non-Functional Test Requirements

- migration up/down test in CI
- runtime smoke checks in every deployment environment
- security negative tests for unauthorized and cross-user access
- performance sanity checks on critical query paths
- analytics event schema checks for core tracked events (`docs/product-analytics.md`)

---

## Merge Gate Minimum

No merge is allowed unless all are true:

- lint/type checks pass
- unit tests pass
- required integration tests pass
- at least one runtime smoke check passes
- changed API behavior is covered by API contract test

---

## Test Data Rules

- use deterministic test fixtures
- separate synthetic data from any real user data
- include multilingual examples (EN/IT/DE) for extraction and query tests

---

## Ownership

- feature author owns new/updated tests
- reviewer verifies test relevance, not just pass/fail
- failing flaky tests must be fixed or quarantined with explicit ticket and deadline
