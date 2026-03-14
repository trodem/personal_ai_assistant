# Security Threat Model (MVP)

## Purpose

Capture primary threats and required controls before and during implementation.

This document complements:

- `docs/risk-analysis.md`
- `docs/error-model.md`
- `docs/operations-runbook.md`
- `docs/rbac-matrix.md`

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
- backend API <-> Supabase platform services (Auth, Postgres, Storage)
- backend API <-> external providers (OpenAI, Stripe)

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

### Admin privilege abuse

Risk:

- unauthorized or excessive privileged actions on user accounts

Controls:

- strict RBAC (`user` vs `admin` vs `author`) on privileged endpoints
- audit log for every admin action (who/when/target/change)
- dual review for high-impact admin operations where feasible
- explicit policy and tests for account status transitions (`active`, `suspended`, `canceled`)
- explicit policy and tests for role transitions (`user` <-> `admin`) by `author` only
- reject self-targeted destructive author actions (self-role-change, self-suspend, self-cancel)
- enforce "last active author" protection invariant

---

### Notification abuse / spoofing

Risk:

- fake or repeated security/billing emails causing trust or phishing issues

Controls:

- send notifications only from backend trusted triggers
- deduplicate/retry controls with delivery logs
- clear signed sender domain and template governance

---

### Role-based billing exemption abuse

Risk:

- unauthorized role elevation to avoid subscription payment

Controls:

- author-only role transition endpoint
- immutable role-to-plan policy checks (`admin`/`author` => `premium` + billing-exempt)
- audit and alerting on every privileged role transition

---

### Token misuse / auth bypass

Risk:

- forged/expired tokens accepted

Controls:

- provider JWT verification with issuer/audience checks
- short token lifetime and secure key rotation
- mandatory `401` on invalid/missing tokens

---

### Account takeover

Risk:

- compromised credentials used to access user/admin accounts

Controls:

- support OAuth SSO for trusted providers (`Google`, `Apple`)
- 2FA/TOTP support for all users
- mandatory 2FA for `admin` and `author`
- re-auth + 2FA challenge for sensitive security changes

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
- admin/author RBAC tests pass
- endpoint-role permissions are aligned with `docs/rbac-matrix.md`
- input validation tests pass
- no secret found in logs/code
- attachment security checks pass

---

## Governance

- review this threat model at each milestone end mini-audit
- create ADR entries for major security design decisions
