# Multi-Tenancy and Data Isolation Policy

## Purpose

Define tenant-level isolation rules for B2B/organization scenarios.

---

## Scope

Applies to:

- organization accounts (future B2B tier)
- tenant-scoped users, data, and operations
- API authorization and data-access boundaries

---

## Isolation Model

MVP+ design target: logical multi-tenancy with strict tenant boundaries.

Core identifiers:

- `tenant_id`
- `user_id`

All tenant-aware entities must include `tenant_id`.

---

## Access Rules

- every request is evaluated with `(tenant_id, user_id)` scope
- cross-tenant access is always forbidden
- tenant admins can only manage users/resources in their own tenant
- global platform roles (if any) must be explicitly separated from tenant roles

---

## Data and Query Rules

- every repository query must filter by `tenant_id` and `user_id` where applicable
- background jobs must preserve tenant context
- vector/semantic retrieval must be tenant-scoped
- caches must be tenant-scoped (and user-scoped where required)

---

## Operational Rules

- audit logs must include `tenant_id` for tenant-scoped actions
- metrics/dashboards should support tenant segmentation
- incident triage must identify impacted tenant(s)

---

## Security Controls

- mandatory negative tests for cross-tenant access attempts
- strict authorization checks on all tenant-aware endpoints
- no shared storage paths without tenant partitioning

---

## Governance

- B2B/multi-tenant changes must update this document, `docs/rbac-matrix.md`, and `TODO.md`
- architecture changes must keep alignment with `PROJECT_CONTEXT.md`
