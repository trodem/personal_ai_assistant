# Trial and Freemium Management Policy

## Purpose

Define trial lifecycle, freemium limits, and discount/coupon controls.

---

## Scope

Applies to:

- free/trial/premium plan transitions
- trial eligibility and expiration
- coupon and temporary discount logic

---

## Plan States

- `free`
- `trial`
- `premium`

Role lock policy still applies:

- `admin` and `author` remain `premium` and billing-exempt

---

## Trial Rules (MVP)

- one trial per eligible user account
- explicit trial duration configuration (for example 7 or 14 days)
- automatic transition on trial expiry according to policy
- trial start/end timestamps must be auditable

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

---

## Metrics

- trial activation rate
- trial-to-premium conversion rate
- coupon redemption rate
- discounted-user retention after 30 days

---

## Governance

- trial/coupon policy changes must update this document, API spec, and `CHANGELOG.md`
