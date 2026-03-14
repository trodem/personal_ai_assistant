# Governance Review Cadence (MVP)

## Standard Cadence
- Mandatory review at each milestone mini-audit.

## Scope
Review applies at minimum to:
- `docs/testing-strategy.md`
- `docs/environment-matrix.md`
- `docs/error-model.md`
- `docs/operations-runbook.md`
- `docs/security-threat-model.md`

## Additional Review Triggers
- Any security-sensitive change.
- Any API contract/error-model change.
- Any auth/RBAC/policy change.
- Any incident postmortem requiring governance updates.

## Review Checklist (Minimum)
1. Confirm no contradictions with `PROJECT_CONTEXT.md`.
2. Confirm alignment with current `TODO.md` execution state.
3. Confirm operational procedures still match implemented behavior.
4. Record required updates in same iteration when feasible.
