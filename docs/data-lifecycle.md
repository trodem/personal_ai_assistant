# Data Lifecycle and Deletion Policy

## Purpose

Define retention, deletion, and right-to-be-forgotten workflows.

---

## Scope

Applies to:

- user account closure/cancellation
- GDPR delete/export requests
- orphan and stale data cleanup jobs
- storage, database, and derived artifacts (embeddings/cache)

---

## Lifecycle States

- active
- canceled_pending_deletion
- deletion_scheduled
- deletion_completed

---

## Deletion Triggers

- explicit user deletion request
- account closure with configured retention expiry
- policy-based cleanup for orphaned or stale data

---

## Deletion Targets

Deletion workflow must cover:

- memories and memory versions
- attachments and storage objects
- embeddings/vector rows
- notification history (per policy)
- cache artifacts

Billing/legal records are retained only where legally required and with minimal data.

---

## Automation Rules

- deletion jobs must run automatically on schedule
- deletion jobs must be idempotent and auditable
- failed deletions must retry with bounded backoff
- completion/failure outcomes must be logged and monitored

---

## Right to be Forgotten (GDPR)

- user can request full deletion
- system must provide deletion confirmation when completed
- deletion SLA must be documented and tracked
- exports must be available before destructive deletion when requested

---

## Safety and Compliance

- no partial deletion across DB/storage/indexes
- all delete operations require traceable audit record
- deletion policy must be reflected in user-facing legal/privacy docs

---

## Governance

- lifecycle/deletion changes must update this document, `TODO.md`, and `CHANGELOG.md`
- policy must remain aligned with `docs/security-threat-model.md` and `docs/operations-runbook.md`
