# Soft-Delete and Audit Trail Strategy (Baseline)

## Goal
Ensure sensitive memory operations (`update` / `delete`) preserve traceability and avoid irreversible data loss.

## Soft-Delete Policy
- `memories` uses logical deletion fields:
  - `deleted_at` (`timestamptz`, nullable)
  - `deleted_by_user_id` (`uuid`, nullable)
  - `delete_reason` (`text`, nullable)
- Active memories are records with `deleted_at IS NULL`.
- Physical deletion is not the default runtime path.

## Audit Trail Policy
- `memory_audit_log` records sensitive actions:
  - `update`
  - `delete`
  - `restore`
- Audit record includes:
  - actor user (`actor_user_id`)
  - target memory (`memory_id`)
  - optional version linkage (`previous_version_id`, `new_version_id`)
  - structured `details` JSON
  - immutable `created_at`

## Schema Baseline
- Migration: `backend/alembic/versions/20260315_0008_soft_delete_and_audit_strategy.py`
- Includes FK integrity and query indexes for operational traceability.
