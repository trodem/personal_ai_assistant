# Data Portability Policy

## Purpose

Define user-facing export capabilities for personal data portability.

---

## Scope

Export includes user-owned data:

- memories and memory versions
- attachments metadata
- question/answer history
- settings/profile metadata
- subscription and notification preference metadata

---

## Supported Formats (MVP)

- `json` (full-fidelity structured export)
- `csv` (tabular summaries where applicable)
- `pdf` (human-readable report bundle)

---

## Export Workflow

1. user requests export with format selection
2. backend creates asynchronous export job
3. user polls export status
4. when ready, user receives temporary signed download URL

---

## Security and Privacy Rules

- export is always scoped to requesting authenticated user
- export files use short-lived signed URLs
- export generation and download are audit-logged
- sensitive fields must be handled according to sanitization/privacy policies

---

## Operational Rules

- export jobs must be idempotent
- failed jobs retry with bounded backoff
- export artifacts are auto-deleted after retention window

---

## Governance

- portability changes must update this document, API contract, and `CHANGELOG.md`
