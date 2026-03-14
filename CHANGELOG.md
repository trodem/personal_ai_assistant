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

---

## Changelog Update Rule

- Update this file whenever a change is user-visible or developer-relevant.
- Prefer updating `Unreleased` in the same PR/iteration as the change.
- If a changelog update is skipped, document the reason in the PR notes.
