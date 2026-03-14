# Churn Management Policy

## Purpose

Define proactive and reactive churn-prevention workflows.

---

## Scope

Applies to:

- subscription users (`free` and `premium`)
- cancellation intent flows
- retention campaigns and offers

---

## Churn Signals (MVP)

- drop in weekly active usage
- drop in memory creation frequency
- repeated no-result/low-satisfaction feedback
- downgrade intent and cancellation preview usage

---

## Risk Scoring

- compute churn risk score per user periodically
- score categories: `low`, `medium`, `high`
- score must be explainable through signal breakdown

---

## Retention Actions

For medium/high churn risk users:

- in-app nudges focused on product value
- contextual recovery prompts (for example onboarding refresh, feature tips)
- targeted retention offers where billing policy allows

For cancel intent users:

- mandatory reason capture
- show tailored alternatives (pause/downgrade/coupon where enabled)
- final confirm step before cancel

---

## Guardrails

- no dark patterns
- no retention action that violates role-based billing lock
- transparent messaging for offers and eligibility

---

## Metrics

- churn risk distribution
- cancel-preview to retained conversion
- cancellation completion rate
- retained users after intervention (7/30 day windows)

Metrics must integrate with `docs/product-analytics.md`.

---

## Governance

- changes to churn logic or offers must update this document and `CHANGELOG.md`
