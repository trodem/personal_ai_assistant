# Security Threat Model (MVP)

## Purpose

Capture primary threats and required controls before and during implementation.

This document complements:

- `docs/risk-analysis.md`
- `docs/error-model.md`
- `docs/operations-runbook.md`

---

## Assets to Protect

- user memories and structured data
- authentication tokens and session context
- attachments and file metadata
- API keys and infrastructure secrets
- billing/subscription state

---

## Trust Boundaries

- mobile client <-> backend API
- backend API <-> external providers (OpenAI, Clerk, Stripe, storage)
- backend API <-> database

All boundaries require explicit authentication and validation.

---

## Top Threats and Controls

### Cross-user data access

Risk:

- one user reading/modifying another user's data

Controls:

- strict `user_id` scoping in every data query
- auth middleware on all protected endpoints
- negative tests for cross-user access

---

### Token misuse / auth bypass

Risk:

- forged/expired tokens accepted

Controls:

- provider JWT verification with issuer/audience checks
- short token lifetime and secure key rotation
- mandatory `401` on invalid/missing tokens

---

### Prompt/data leakage

Risk:

- sensitive data leaked to logs or AI prompts beyond necessity

Controls:

- minimize prompt context
- redact sensitive fields from logs
- structured logging with secret filtering

---

### Malicious file uploads

Risk:

- executable/malware file upload abuse

Controls:

- file type/size validation
- allow-list only receipt photo MIME types (`image/jpeg`, `image/png`, `image/webp`, `image/heic`)
- content scanning where available
- signed URL access with expiry

---

### Abuse and denial of service

Risk:

- endpoint flooding and cost abuse

Controls:

- rate limiting
- AI usage quotas
- anomaly alerts on traffic/cost spikes

---

## Verification Checklist

- auth negative tests pass
- cross-user authorization tests pass
- input validation tests pass
- no secret found in logs/code
- attachment security checks pass

---

## Governance

- review this threat model at each milestone end mini-audit
- create ADR entries for major security design decisions
