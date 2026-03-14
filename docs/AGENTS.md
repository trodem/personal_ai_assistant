# Rules - Personal AI Assistant

## Project Overview

This repository contains the code and architecture for the Personal AI Assistant platform.

The project follows an MVP-first development strategy.

The architecture and system design are defined in the `docs/` directory.

These documents represent the source of truth for the project.

---

# Document Usage Map (Mandatory)

The agent must use documents by purpose, not randomly.

Precedence order when conflicts appear:

1. `PROJECT_CONTEXT.md`
2. `docs/architecture.md` + `docs/system-architecture.md`
3. `docs/contract.md` + `docs/database-schema.md` + `docs/ai-pipeline.md`
4. `docs/query-contract.md` + `docs/ai-ux-contract.md`
5. `specs/api.yaml` + `specs/memory-extraction.md`
6. `docs/development-roadmap.md` + `TODO.md`
7. operational docs:
- `docs/testing-strategy.md`
- `docs/environment-matrix.md`
- `docs/error-model.md`
- `docs/operations-runbook.md`
- `docs/security-threat-model.md`
- `docs/rbac-matrix.md`
- `docs/product-analytics.md`
- `docs/model-registry.md`
- `docs/llmops-dashboard-spec.md`
- `docs/coding-standards.md`
- `CONTRIBUTING.md`

When to consult each document:

- API change: read `specs/api.yaml` and `docs/error-model.md`
- memory extraction/storage change: read `docs/contract.md`, `docs/domain-model.md`, `specs/memory-extraction.md`, `docs/database-schema.md`
- question-answering change: read `docs/query-contract.md`, `docs/ai-pipeline.md`, `docs/error-model.md`, `specs/api.yaml`
- AI UX behavior change: read `docs/ai-ux-contract.md`, `docs/contract.md`, and `docs/error-model.md`
- AI model/prompt change: read `docs/model-registry.md`, `docs/ai-cost-control.md`, and `specs/memory-extraction.md`
- auth/security change: read `docs/security-threat-model.md` and `docs/risk-analysis.md`
- auth/role/permission change: read `docs/rbac-matrix.md` and `docs/security-threat-model.md` before implementation
- infra/environment/deploy change: read `docs/environment-matrix.md` and `docs/operations-runbook.md`
- test strategy/quality gate change: read `docs/testing-strategy.md` and `TODO.md`
- analytics/observability behavior change: read `docs/product-analytics.md`, `docs/error-model.md`, and `TODO.md`
- LLMOps/dashboard/alerting change: read `docs/llmops-dashboard-spec.md`, `docs/ai-cost-control.md`, and `docs/operations-runbook.md`
- code-structure/style/logging change: read `docs/coding-standards.md`, `CONTRIBUTING.md`, and `TODO.md`
- architecture-level tradeoff: add/update ADR in `ADR/`

If a conflict remains unresolved after precedence, the agent must stop and ask the user.

Alignment Invariant (non-negotiable):

- every change must be aligned across all impacted files (`PROJECT_CONTEXT.md`, `docs/`, `specs/`, `TODO.md`)
- no partial update is allowed if it creates contradictions
- if full alignment cannot be completed in the same change, the agent must stop and report the blocker

---

# Documentation Protection

The following directories are protected:

docs/
specs/
ADR/

AI agents are not allowed to modify these files unless the user explicitly requests documentation changes.

Agents must treat these files as read-only design specifications by default.

---

# Allowed Modifications

Agents are allowed to modify:

backend/
mobile/
infra/
scripts/

They may also create new files when necessary for implementation.

---

# Development Workflow

Agents must always follow the project roadmap defined in:

TODO.md

Rules:

- work only on the first incomplete task
- implement step-by-step
- do not skip tasks
- do not refactor unrelated code
- run a mini-audit at the end of each milestone before moving forward

Mini-audit checklist (mandatory):

- verify milestone output is aligned with `PROJECT_CONTEXT.md`, `docs/`, and `specs/`
- verify no architecture rule was violated
- verify security and user-isolation requirements remain enforced
- verify API and implementation remain consistent for touched endpoints
- verify document-trigger usage was respected for changed scope
- verify `CHANGELOG.md` was updated when relevant
- document any gaps/blockers before starting the next milestone

---

# Code Style Rules

- keep modules small
- avoid large files
- separate responsibilities
- prefer simple solutions
- avoid premature optimization
- use reusable Flutter components for repeated UI patterns
- centralize Flutter style tokens; avoid scattered hardcoded colors/styles
- keep UI logic and business logic separated
- keep identifiers/comments/docs in code exclusively in English
- maintain production-grade backend logging with traceability and redaction
- respect architecture lint/static rules that prevent business logic in Flutter widgets/screens
- keep pre-commit hooks green before finalizing implementation

---

# Safety Rules

Agents must never:

- delete existing database structures
- remove authentication logic
- expose secrets
- disable security checks

---

# Architecture Rules

Agents must follow the architecture defined in:

docs/architecture.md

Key principles:

- voice-first interaction
- structured memory storage
- AI-assisted extraction
- semantic search with embeddings
- cloud-based architecture

Agents must not change the architecture.

---

# AI Behavior Rules

AI features must follow the memory contract defined in:

docs/contract.md

Key rules:

- memories require user confirmation before saving
- incomplete data triggers clarification questions
- memories contain structured data and embeddings

---

# Refactoring Rules

Agents may refactor code only if:

- it improves clarity
- it does not change behavior
- it does not modify architecture

Large refactors require user approval.

---

# Dependency Rules

Agents must avoid adding unnecessary dependencies.

Any new dependency must be justified by functionality.

---

# Security Rules

- validate all inputs
- verify authentication tokens
- protect user data
- avoid insecure libraries
