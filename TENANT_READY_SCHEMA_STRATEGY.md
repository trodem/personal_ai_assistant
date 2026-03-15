# Tenant-Ready Schema Strategy (Baseline)

## Goal
Prepare PostgreSQL schema for B2B multi-tenant isolation without breaking current single-tenant development flow.

## Baseline Decisions
- Add `tenant_id` to user-scoped core tables:
  - `users`
  - `memories`
  - `memory_versions`
  - `attachments`
  - `embeddings`
  - `qa_interactions`
- Keep `tenant_id` non-null with safe default: `tenant-default`.
- Add `CHECK (length(tenant_id) > 0)` on each table.
- Add index `ix_<table>_tenant_id` to support tenant-scoped filtering.

## Migration Path
- Migration file: `backend/alembic/versions/20260315_0007_prepare_tenant_ready_schema.py`
- Scope is schema preparation only; strict tenant policy and composite constraints are handled in subsequent tasks.

## Runtime Query Contract
- Repository/API queries must include both:
  - `tenant_id`
  - `user_id`
- No cross-tenant data access is allowed.
