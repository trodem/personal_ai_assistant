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
- Multi-language planning made explicit with MVP language matrix (`en`, `it`, `de`), deterministic fallback (`en`), settings-level `preferred_language` contract, and aligned roadmap/query/testing/TODO coverage.
- Guided onboarding planning expanded with explicit first-run step sequence, permission UX, skip/resume behavior, persisted completion state, and analytics funnel instrumentation.
- Added `docs/model-registry.md` as canonical model/prompt governance source, with rollout/rollback policy and required mapping of AI use-cases to model/prompt versions; linked across AGENTS, TODO, roadmap, architecture, cost-control, and project context docs.
- Added `docs/ai-ux-contract.md` to formalize AI-specific UX rules (clarification cadence, confirmation flow, answer explainability, state/error UX, accessibility/localization), with alignment updates across AGENTS, TODO, roadmap, architecture, and project context.
- Added `docs/llmops-dashboard-spec.md` with required dashboards, metric dimensions, MVP alert thresholds, and runbook integration for AI operations; linked across AGENTS, TODO, operations, cost-control, architecture, and project context.
- User settings panel planning completed with payment-method management scope (list masked methods, setup-intent flow, set default, remove), with aligned API contract, RBAC policy, roadmap, and architecture docs.
- Added streaming question-response planning with SSE endpoint (`POST /api/v1/question/stream`), UX typing mode, fallback-to-non-stream behavior, RBAC alignment, and streaming-specific API test requirements.
- Added explicit AI content safety and data sanitization governance via `docs/content-moderation.md` and `docs/data-sanitization.md`, with aligned TODO/security/error-model/architecture/analytics/document-routing updates.
- Added planning for AI answer feedback loop (`Like`/`Dislike`) and churn-management cancellation flow (reason capture + retention preview), including API contract, RBAC, roadmap, UX, monetization, and analytics alignment.
- Added formal rollout/lifecycle governance docs: `docs/feature-flags-experiments.md` and `docs/api-compatibility.md`, with alignment across AGENTS, TODO, roadmap, architecture, decisions, context, and analytics event taxonomy.
- Added `docs/semantic-caching.md` with user-scoped cache strategy, thresholds/TTL, invalidation rules, and quality guardrails; aligned across AGENTS, TODO, query contract, roadmap, architecture, cost-control, LLMOps, and context docs.
- Added `docs/multi-tenancy.md` and `docs/data-lifecycle.md` to formalize B2B tenant isolation and automated retention/deletion workflows (including right-to-be-forgotten), with alignment updates across AGENTS, TODO, roadmap, architecture, security threat model, context, and file structure docs.
- Expanded churn/trial/portability planning with proactive churn-risk policy, trial/coupon governance, and data portability export policy (`json`/`csv`/`pdf`) including API contracts, RBAC, analytics KPIs, error codes, roadmap, and architecture/context alignment.

---

## Changelog Update Rule

- Update this file whenever a change is user-visible or developer-relevant.
- Prefer updating `Unreleased` in the same PR/iteration as the change.
- If a changelog update is skipped, document the reason in the PR notes.
