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
- API contracts, roadmap, bootstrap, RBAC matrix, and OpenAPI spec aligned on versioned endpoint namespace (`/api/v1/...`) with explicit versioning policy in architecture decisions.
- Added explicit text-question API contract (`POST /api/v1/question`) and aligned roadmap, architecture, RBAC matrix, and query contract references.
- Attachment lifecycle state machine normalized across docs and OpenAPI to include `persisted` state.
- Added explicit "Hard blockers before Sprint 1 start" checklist in `TODO.md` for external account/access prerequisites.
- Authentication planning expanded with explicit SSO policy (Google/Apple) and 2FA policy (mandatory for `admin`/`author`, optional for `user`) across TODO, architecture, decisions, bootstrap, and security threat model.
- Security settings API contract extended to cover 2FA operations (`enable_2fa`, `disable_2fa`, `verify_2fa`) and user settings now include `mfa_enabled`/`auth_provider`.
- Infrastructure scalability planning made explicit: cloud multi-instance backend, managed load balancer, health-check routing, autoscaling policy, and zero-downtime rollout requirements across roadmap/TODO/environment matrix.
- Notification system planning expanded from email-only to multi-channel (`in-app`, `push`, `email`) with settings preferences, in-app feed/read endpoints, RBAC alignment, and architecture/roadmap/TODO coverage.
- Added `docs/product-analytics.md` with canonical event taxonomy, funnels, KPI mapping, payload schema rules, and privacy constraints; linked into AGENTS routing, TODO quality gates, roadmap, architecture context, and testing strategy.

---

## Changelog Update Rule

- Update this file whenever a change is user-visible or developer-relevant.
- Prefer updating `Unreleased` in the same PR/iteration as the change.
- If a changelog update is skipped, document the reason in the PR notes.
