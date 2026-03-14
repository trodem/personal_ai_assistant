# Feature Flags and Experimentation Policy

## Purpose

Define safe rollout controls and experiment rules for product, UX, and AI behavior changes.

---

## Scope

Applies to:

- frontend feature exposure
- backend capability rollout
- AI prompt/model variant experiments
- gradual and cohort-based releases

---

## Feature Flag Rules

- every non-trivial new feature must support flag-based enable/disable in staging/prod
- flags must be evaluated at runtime (no app restart required)
- every flag must define:
- `flag_key`
- owner
- default state per environment
- target cohorts (role/plan/app-version/percentage)
- kill-switch behavior
- expiration date (to avoid stale flags)

---

## Targeting Dimensions (MVP)

- user role (`user`, `admin`, `author`)
- subscription plan (`free`, `premium`)
- app version
- deterministic user-percentage rollout
- explicit allow-list/deny-list user IDs (staging/support use)

---

## A/B Experiment Rules

- experiments must have:
- `experiment_key`
- hypothesis
- primary metric
- guardrail metrics
- start/end criteria
- rollback criteria

- assignment must be deterministic and sticky per user/session policy
- experiment variants must be versioned and auditable
- no experiment may violate security/privacy policies

---

## AI Experiment Rules

- prompt/model experiments must reference `docs/model-registry.md`
- each variant must map to explicit model/prompt versions
- unsafe quality/cost regressions must trigger immediate rollback

---

## Required Metrics

For each experiment track:

- exposure count per variant
- conversion/success metric (primary)
- retention/churn impact
- cost impact (tokens/cost per request when AI-related)
- error/latency guardrails

---

## Governance

- feature flag and experiment changes must update this document, `TODO.md`, and `CHANGELOG.md`
- stale flags must be removed after experiment/rollout completion
