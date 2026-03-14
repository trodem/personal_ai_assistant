# Data Sanitization and Anonymization Policy

## Purpose

Define how sensitive data is minimized/redacted before sending context to AI providers.

---

## Scope

Applies to:

- prompt context sent to LLM providers
- logs and analytics payloads
- support/debug traces

---

## Core Rules

- send only minimal context required for task completion
- redact direct identifiers when not required for answer quality
- never send secrets/tokens/credentials to AI providers
- preserve deterministic placeholders when redacting (for traceability)

---

## Redaction Classes (MVP)

- email addresses
- phone numbers
- payment card numbers
- national IDs/passport IDs
- exact street addresses (unless explicitly required by memory meaning)

---

## Prompt Sanitization Flow

1. classify text fields for sensitive patterns
2. apply deterministic masking/redaction
3. keep mapping only in backend transient context (never exposed in logs)
4. send sanitized context to provider

---

## Logging and Analytics Rules

- logs must store redacted values only
- analytics must use IDs/coarse categories, not raw PII
- error payloads must not leak sensitive fields

---

## Error and Event Mapping

Error codes (see `docs/error-model.md`):

- `privacy.sensitive_data_detected`

Analytics events (see `docs/product-analytics.md`):

- `prompt_sanitized`
- `privacy_redaction_applied`

---

## Governance

- sanitization rule changes require updates to this file, tests, and changelog
- policy must stay aligned with GDPR baseline in `TODO.md` and `docs/security-threat-model.md`
