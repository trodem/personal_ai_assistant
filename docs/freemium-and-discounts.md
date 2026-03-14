# Freemium and Discount Management Policy

## Purpose

Define freemium limits and discount/coupon controls.

---

## Scope

Applies to:

- free/premium plan transitions
- coupon and temporary discount logic

---

## Plan States

- `free`
- `premium`

Role lock policy still applies:

- `admin` and `author` remain `premium` and billing-exempt

---

## Coupon and Discount Rules

- coupon codes must have validity window and usage limits
- coupon eligibility must be deterministic and auditable
- temporary discounts must include start/end date and target scope
- abuse controls required (rate limits, duplicate redemption prevention)

---

## Billing Guardrails

- no coupon flow for role-locked billing-exempt accounts (`admin`, `author`)
- failed coupon application must return deterministic error code
- all plan-price changes must preserve compatibility with active subscriptions
- self-service plan change endpoint supports only `free <-> premium`

---

## Metrics

- coupon redemption rate
- discounted-user retention after 30 days

---

## Governance

- coupon/pricing policy changes must update this document, API spec, and `CHANGELOG.md`
