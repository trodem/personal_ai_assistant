# Contributing Guide

## Purpose

Define a predictable workflow for implementing changes without architectural drift.

---

## Ground Rules

- follow `TODO.md` milestone order
- work only on the first incomplete task unless explicitly redirected
- avoid unrelated refactors
- keep changes small and reviewable
- follow `docs/coding-standards.md` for Flutter/FastAPI implementation quality

---

## Branch and Commit Rules

- branch naming: `feature/<scope>`, `fix/<scope>`, `chore/<scope>`
- commit messages should be clear and scoped
- one logical change per commit where possible

---

## Pull Request Checklist

Before opening PR:

- [ ] lint/type checks pass
- [ ] relevant tests added/updated and passing
- [ ] docs updated when behavior/contract changes
- [ ] no secrets in code/config
- [ ] changed endpoints aligned with `specs/api.yaml`
- [ ] role/permission changes aligned with `docs/rbac-matrix.md`
- [ ] changelog updated in `CHANGELOG.md` when applicable
- [ ] pre-commit hooks run locally without violations
- [ ] mini-audit notes added for milestone-level changes

---

## Review Criteria

Reviewers should verify:

- architecture alignment with `PROJECT_CONTEXT.md` and `docs/`
- security/user-isolation correctness
- RBAC correctness and role-policy alignment (`docs/rbac-matrix.md`)
- error model consistency (`docs/error-model.md`)
- test adequacy for risk level of change
- coding standards alignment (`docs/coding-standards.md`)
- architecture lint rules respected (no business logic in Flutter widgets/screens)
- backend logging contract tests updated/passing when log format changed

---

## Definition of Ready (for implementation)

A task is ready when:

- dependencies are completed
- acceptance criteria are explicit
- environment/service prerequisites are available

---

## Definition of Done (for merge)

Done means:

- functionality works as designed
- automated checks pass
- no unresolved blocker for next dependency step
