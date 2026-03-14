# API Error Model

## Purpose

Define a consistent API error contract across backend endpoints.

This document prevents ad-hoc error formats and makes client behavior predictable.

---

## Standard Error Schema

Every non-2xx response must use:

```json
{
  "error": {
    "code": "string_code",
    "message": "Human-readable summary",
    "details": {},
    "request_id": "uuid-or-trace-id",
    "retryable": false
  }
}
```

---

## Error Code Conventions

- format: `domain.reason`
- stable and machine-readable
- message can evolve, code should remain stable

Examples:

- `auth.missing_token`
- `auth.invalid_token`
- `auth.forbidden`
- `auth.last_author_protection`
- `auth.self_role_change_forbidden`
- `memory.validation_failed`
- `memory.confirmation_required`
- `memory.missing_required_fields`
- `query.ambiguous_intent`
- `query.no_results`
- `storage.upload_failed`
- `storage.unsupported_file_type`
- `storage.attachment_orphaned`
- `ocr.processing_failed`
- `ocr.low_confidence`
- `moderation.blocked_content`
- `moderation.review_required`
- `ai.provider_unavailable`
- `query.stream_unavailable`
- `privacy.sensitive_data_detected`
- `billing.plan_locked_by_role`
- `rate.limit_exceeded`
- `internal.unexpected_error`

---

## HTTP Mapping

| HTTP | Category | Typical codes |
|---|---|---|
| 400 | bad request | `memory.validation_failed` |
| 401 | unauthorized | `auth.missing_token`, `auth.invalid_token` |
| 403 | forbidden | `auth.forbidden`, `auth.last_author_protection`, `auth.self_role_change_forbidden`, `billing.plan_locked_by_role`, `moderation.blocked_content` |
| 404 | not found | `memory.not_found`, `query.no_results` |
| 409 | conflict | `memory.version_conflict` |
| 422 | semantic validation | `memory.confirmation_required`, `memory.missing_required_fields`, `query.ambiguous_intent`, `storage.unsupported_file_type`, `ocr.low_confidence`, `moderation.review_required`, `privacy.sensitive_data_detected` |
| 429 | rate limit | `rate.limit_exceeded` |
| 500 | internal | `internal.unexpected_error` |
| 502/503 | dependency outage | `ai.provider_unavailable`, `db.unavailable`, `query.stream_unavailable` |

---

## Retry Rules

- `retryable=true` only for transient dependency failures/timeouts/rate-limit windows
- client must never retry validation/auth errors without user action

---

## Logging Rules

- include `request_id` in all error logs
- never log secrets, tokens, or full sensitive payloads
- include error code in structured logs

---

## Contract Governance

- any new error code must be added here
- API contract updates in `specs/api.yaml` must stay consistent with this model
