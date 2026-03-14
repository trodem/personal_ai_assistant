# Changelog

All notable changes to this project should be documented in this file.

Format inspired by Keep a Changelog and Semantic Versioning principles.

## [Unreleased]

### Added
- Coding standards document for Flutter/FastAPI quality, logging, and language rules.
- Receipt-photo attachment and OCR workflow hardening rules across docs/specs.
- Alignment invariant and documentation consistency requirements.
- Admin and Author role architecture with RBAC-protected management endpoints.
- Author safety policy (self-change restrictions and last-active-author protection).

### Changed
- Architecture and governance docs aligned to receipt-photo-only attachment policy.
- README and bootstrap guidance aligned to confirmation-first memory persistence.
- Billing model updated with role-based policy: `admin`/`author` always `premium` and billing-exempt.
- Governance docs now enforce `docs/rbac-matrix.md` as mandatory reference for auth/role/permission changes.
- Bootstrap and agent prompt routing updated to include RBAC-driven role/permission implementation rules.
- Platform stack migrated from Clerk/multi-storage options to Supabase-first (`Supabase Auth` + `Supabase Postgres` + `Supabase Storage`) across planning and architecture docs.
- Project file-structure map updated to include settings/admin/author/billing modules and endpoint files.
- Non-goals wording aligned with receipt-photo-only attachment policy.
- Documentation text normalized to ASCII-safe formatting (pipeline arrows, quotes, currency and dash notation) for consistent readability across environments.
- README completed with operational onboarding sections (official stack, owner checklist, local start, document routing, and governance links).

---

## Changelog Update Rule

- Update this file whenever a change is user-visible or developer-relevant.
- Prefer updating `Unreleased` in the same PR/iteration as the change.
- If a changelog update is skipped, document the reason in the PR notes.
