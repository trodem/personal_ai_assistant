# Contributing Guide

## Purpose

Define a predictable workflow for implementing changes without architectural drift.

---

## Ground Rules

- follow `TODO.md` milestone order
- work only on the first incomplete task unless explicitly redirected
- avoid unrelated refactors
- keep changes small and reviewable

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
- [ ] mini-audit notes added for milestone-level changes

---

## Review Criteria

Reviewers should verify:

- architecture alignment with `PROJECT_CONTEXT.md` and `docs/`
- security/user-isolation correctness
- error model consistency (`docs/error-model.md`)
- test adequacy for risk level of change

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
