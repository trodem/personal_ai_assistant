# Changelog

All notable changes to this project should be documented in this file.

Format inspired by Keep a Changelog and Semantic Versioning principles.

## [Unreleased]

### Added
- Added Alembic migration baseline (`backend/alembic`) and `scripts/migration-smoke-check.ps1` to verify PostgreSQL migration upgrade/downgrade/restore flow in local Docker.
- Added `scripts/storage-upload-download-smoke.ps1` to validate Supabase Storage object lifecycle (`upload -> download -> content check -> delete`) against the configured receipts bucket.
- Added `PRIVACY_POLICY_BASELINE.md` with MVP privacy baseline scope, data categories, retention/deletion process, security posture, and user rights/export-deletion commitments.
- Added `TERMS_BASELINE.md` with MVP terms baseline for account usage, acceptable use, AI-output limitations, billing baseline, and liability/contact placeholders.
- Added `SUPPORT_CONTACT_AND_INCIDENT_OWNER.md` defining MVP support contact, incident owner/backup owner, and baseline escalation flow.
- Added `scripts/env-example-completeness-check.ps1` and wired it into `scripts/quality-check.ps1` to enforce `.env.example` and `docker-compose.yml` runtime variable completeness for local boot.
- Baseline `docker-compose.yml` with local `backend` and `postgres` (`pgvector`) services so `docker compose config` validates successfully.
- Added container healthchecks for backend and postgres so both services report healthy in `docker compose ps`.
- Added `scripts/quality-check.ps1` plus backend baseline test (`backend/tests/test_compose_baseline.py`) to run lint/test/build checks for touched components.
- Added runtime smoke verification for local stack (Invoke-WebRequest http://localhost:8000 expecting 200) and validated running healthy services via docker compose ps.
- Aligned .env.example, docker-compose.yml, and local setup instructions in README.md (shared API_PORT and POSTGRES_* variables with matching connection details).
- Added integration runtime tests (`backend/tests/test_runtime_integration.py`) and wired them into `scripts/quality-check.ps1` with automatic container startup and health waiting.
- Added GitHub Actions CI workflow (.github/workflows/ci.yml) to run scripts/quality-check.ps1 on push and pull_request before merge.
- Added modular FastAPI backend baseline with structured JSON logging (`request_id`, `trace_id`, optional `user_id`), Prometheus-style `/metrics`, and standardized API error schema/handlers aligned to `docs/error-model.md`.
- Added LLMOps-aligned metrics foundation (`backend/app/core/llmops.py`) with required dimensions and MVP alert thresholds exposed via `/metrics` and covered by automated tests.
- Added product-analytics contract foundation (`backend/app/core/analytics.py`) with snake_case schema validation and automatic operational events (`api_error_4xx`/`api_error_5xx`) emitted in structured logs.
- Added production-grade log redaction in `backend/app/core/logging_config.py` (secret/token/password/email masking) with contract tests in `backend/tests/test_logging_redaction.py`.
- Added security-by-default backend baseline with bearer-token validation and strict user_id-scoped memory access (GET /api/v1/memories) plus negative auth tests (401 missing/invalid token).
- Added strict tenant+user isolation for tenant-aware access (`tenant_id` claim + `x-tenant-id` header enforcement, cross-tenant rejection) on `GET /api/v1/memories`, with dedicated negative tests.
- Added Supabase-auth smoke tooling (`scripts/supabase-auth-smoke.ps1`) and JWT validation compatibility updates to verify `401` without token and `200` with a valid Supabase access token on protected endpoints.
- Added Supabase JWT ES256/JWKS verification path in auth plus backend compose env wiring (SUPABASE_URL, SUPABASE_JWT_SECRET) to support real token validation.
- Validated Supabase email/password login flow end-to-end via `scripts/supabase-auth-smoke.ps1`.
- Added MFA policy enforcement for privileged roles (`admin`/`author`) on admin endpoints with explicit `auth.mfa_required` blocking and integration tests.
- Aligned OpenAPI spec with implemented endpoints and auth guards (`/health/live`, `/health/ready`, `/metrics`, tenant header semantics on protected tenant-aware routes).
- Hardened FastAPI Swagger/OpenAPI metadata for implemented endpoints (typed response models, operation summaries/descriptions, documented 401/403 responses, and bearer security scheme exposure) with automated `/openapi.json` regression tests.
- Added API backward-compatibility regression tests (`backend/tests/test_api_backward_compatibility.py`) to enforce v1 path stability and preserve required response fields for current and previously shipped clients.
- Added preferred-language i18n baseline across backend and Flutter labels: `GET /api/v1/me/settings` + `PATCH /api/v1/me/settings/profile` now enforce `en/it/de` with fallback `en`, plus ARB label files (`mobile/lib/l10n/app_{en,it,de}.arb`) and contract tests for backend/UI locale consistency.
- Aligned API error mapping with `docs/error-model.md`: removed undocumented error codes, standardized `404 -> memory.not_found`, `422 -> memory.missing_required_fields`, and added retryable policy for `429/502/503` plus dedicated error-model contract tests.
- Added memory-ingestion E2E baseline with modular extraction service and protected endpoints (`POST /api/v1/voice/memory`, `POST /api/v1/memory`) enforcing clarification for missing fields, explicit confirmation before persistence, and persistence verification via `GET /api/v1/memories`.
- Added question-engine database-first baseline (`POST /api/v1/question`) with deterministic backend aggregation over persisted user memories and no-result fallback, plus tests proving backend-side sum/filter behavior and source-memory traceability.
- Extended question-engine behavior to align with `docs/query-contract.md`: latest/last deterministic lookup, multi-currency separation (no silent conversion), ambiguity handling via `query.ambiguous_intent`, out-of-scope boundary response, no-result Add Memory suggestion, and answer language from `preferred_language` (`en/it/de` fallback `en`).
- Added user-scoped semantic cache policy baseline for question flow with similarity threshold, filter-context-aware cache keys (language/currency/period), volatile/default TTLs (1h/24h), bypass on low confidence/ambiguity, and cache invalidation on memory create; covered by dedicated policy tests.
- Aligned AI UX backend contract for memory flow: one clarification question per turn, explicit AI states (`needs_clarification`, `ready_to_confirm`, `saved`), confirmation actions (`Confirm/Modify/Cancel`), source context (`voice`), and editable absolute datetime in proposal response, with regression tests.
- Added attachments E2E baseline: protected `POST /api/v1/attachments` for receipt-photo upload (image-only validation), deterministic OCR-to-memory-proposal response, explicit confirm-only persistence gate, and authorized signed-URL validation on memory save with attachment lifecycle transition to `persisted`.
- Added attachment lifecycle state-machine verification coverage end-to-end with deterministic status history (`uploaded -> ocr_processing -> proposal_ready -> confirmed -> persisted`) plus OCR failure branch (`failed`, `ocr.processing_failed`) and persistence blocking for non-ready attachments.
- Activated runtime AI telemetry for token usage and estimated cost in LLMOps metrics: added per-use-case counters in `/metrics`, structured `ai_usage_recorded` logs, and instrumentation for memory extraction, receipt OCR extraction, and answer generation flows with automated regression coverage.
- Coding standards document for Flutter/FastAPI quality, logging, and language rules.
- Receipt-photo attachment and OCR workflow hardening rules across docs/specs.
- Alignment invariant and documentation consistency requirements.
- Admin and Author role architecture with RBAC-protected management endpoints.
- Author safety policy (self-change restrictions and last-active-author protection).
- Baseline `.env.example` with Supabase/OpenAI/Stripe and runtime configuration placeholders for local bootstrap.

### Changed
- Marked legal minimum checklist item `Draft privacy policy baseline (data stored, retention, deletion process)` as completed in `TODO.md`.
- Marked legal minimum checklist item `Draft terms baseline for MVP users` as completed in `TODO.md`.
- Marked legal minimum checklist item `Define support contact and incident response owner` as completed in `TODO.md`.
- Completed Day 0 connectivity checks in `TODO.md` by validating OpenAI minimal API call, PostgreSQL connectivity (`select 1`), and Supabase Storage upload/download smoke.
- Completed Day 1 toolchain readiness check in `TODO.md` by confirming local Docker, Python, package manager (`pip`), and Flutter SDK availability.
- Completed Day 1 Docker readiness check in `TODO.md` by validating `docker compose config` and confirming backend/postgres services in healthy state.
- Completed Day 1 local-stack completeness check in `TODO.md` by verifying running `backend` service plus Supabase local `auth`, `postgres+pgvector`, and `storage` services.
- Completed Day 1 environment-config verification in `TODO.md` by passing `.env.example` completeness and environment-matrix checks against current runtime requirements.
- Completed Day 1 smoke-path verification in `TODO.md` (`backend boot -> /health/live 200 -> /health/ready 200 -> DB readiness query`).
- Updated `README.md` with a reproducible local setup command sequence covering Docker/Supabase startup, health checks, OpenAI/Supabase auth checks, migration smoke, storage smoke, and full quality checks; marked the related Day 1 checklist item as completed in `TODO.md`.
- Defined team access-role baseline in `TODO.md` (`author`, `admin`, `developer`, `read-only`) and marked the corresponding access/security setup task as completed.
- Completed environment readiness check `Postgres connection, migration run, and rollback test completed` after validating DB connectivity and running migration smoke (`upgrade -> verify -> downgrade -> verify -> restore`).
- Completed environment readiness check `Object storage upload/download test completed` after running `scripts/storage-upload-download-smoke.ps1` successfully.
- Re-validated OpenAI API key with a minimal live API call via `scripts/openai-account-check.ps1`; marked `OpenAI key validated with a minimal API test call` as completed in `TODO.md`.
- Re-validated Supabase Auth test-user login and protected-token path using `scripts/supabase-auth-smoke.ps1`; marked `Supabase Auth test users and token validation path verified` as completed in `TODO.md`.
- Marked environment readiness checklist item `.env.example completed with all required variables for local startup` as completed after re-validating with `scripts/env-example-completeness-check.ps1`.
- Verified managed Supabase Storage bucket configuration for staging/prod (`receipts` exists and `public=false`) and marked `Supabase Storage buckets configured for staging/prod` plus parent `Object storage ready` as completed in `TODO.md`.
- Verified Supabase local development Storage availability via Supabase CLI (`supabase start` + `supabase status` showing active Storage endpoint) and marked `Supabase local Storage (via Supabase CLI/Docker) for development` as completed in `TODO.md`.
- Verified managed Supabase environment target (`SUPABASE_URL` points to `*.supabase.co`) and successful Supabase Auth/PostgREST reachability checks; marked `Supabase managed Postgres for staging/prod` and parent `PostgreSQL environment ready` as completed in `TODO.md`.
- Verified local PostgreSQL development readiness (`postgres` healthy in Docker and `pg_isready` accepting connections) and marked `Supabase local Postgres (via Supabase CLI/Docker) for development` as completed in `TODO.md`.
- Verified Supabase project reachability across Auth, PostgREST, and Storage via `scripts/supabase-project-reachability-check.ps1` and marked the related prerequisite task as completed in `TODO.md`.
- Verified OpenAI account readiness (API key + billing-enabled request) via `scripts/openai-account-check.ps1` and marked the related prerequisite task as completed in `TODO.md`.
- Verified Git hosting repository access in local workspace via configured `origin` remote and marked the related prerequisite task as completed in `TODO.md`.
- Assigned first primary/backup ownership entry in Day 0 Operational Registry (`OpenAI` row) and marked the related hard blocker as completed in `TODO.md`.
- Expanded local bootstrap configuration with `APP_VERSION`, `APP_CORS_ALLOW_ORIGINS`, `AI_TOKEN_BUDGET_FREE`, and `AI_TOKEN_BUDGET_PREMIUM` in `.env.example` and backend compose env mapping; marked the corresponding hard blocker task as completed in `TODO.md`.
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
- Expanded churn/portability planning with proactive churn-risk policy, coupon governance, and data portability export policy (`json`/`csv`/`pdf`) including API contracts, RBAC, analytics KPIs, error codes, roadmap, and architecture/context alignment.
- Added `docs/completeness-matrix.md` as consolidated planning status matrix (capability -> docs/contracts/TODO coverage) and linked it in AGENTS routing and project file structure.
- OpenAPI subscription schema aligned to freemium policy (`subscription_plan`: `free/premium` in user/admin responses).
- Updated `docs/model-registry.md` with concrete active runtime mappings (`memory_extraction`, `receipt_ocr_extraction`, `answer_generation`) and explicit rollback entries aligned with current backend telemetry identifiers and versions.
- Added active AI cost controls in LLMOps runtime metrics: token budget tracking by plan (usage/utilization/breaches), per-user cost visibility via hashed user metrics, and daily spend spike alert gauges (`warning`/`critical`) based on 7-day baseline comparison.
- Enabled browser CORS preflight support for protected APIs by adding FastAPI `CORSMiddleware` configuration and automated coverage for `OPTIONS` on `/api/v1/memories` with expected CORS headers.
- Added Flutter UI design-system baseline with centralized theme tokens (`colors`, `spacing`, `radii`, `shadows`), reusable widgets (`AppPrimaryButton`, `AppSurfaceCard`), and app bootstrap wired to shared theme to prevent scattered hardcoded style usage; added Flutter analyze/test coverage for the new UI baseline.
- Added `scripts/test-scope-check.ps1` to enforce testing-strategy-aligned scope for touched backend/mobile components (targeted unit/integration/e2e backend suites + Flutter analyze/test in `mobile/`).
- Added `scripts/environment-matrix-check.ps1` and wired it into `scripts/quality-check.ps1` to enforce dev environment/config alignment (`APP_ENV`, Supabase URL wiring, compose env bindings) against `docs/environment-matrix.md`.
- Added `scripts/security-threat-model-check.ps1` and wired it into `scripts/quality-check.ps1` to enforce security threat-model checks (auth/tenant isolation, RBAC+MFA, attachment upload/signed URL authorization, and log redaction).
- Added AI safety enforcement layer (`backend/app/services/ai_safety.py`) with deterministic moderation decisions (`allow/warn/block/review`), pre-input sanitization/redaction for AI paths (voice memory, question, receipt OCR, memory save), moderation analytics events, and policy-aligned error codes (`moderation.blocked_content`, `moderation.review_required`); added `backend/tests/test_ai_safety_alignment.py` and `scripts/ai-safety-check.ps1` (wired into `scripts/quality-check.ps1`).
- Added RBAC alignment checks with `backend/tests/test_rbac_matrix_alignment.py` and `scripts/rbac-check.ps1` (wired into `scripts/quality-check.ps1`), including role access assertions (`user/admin/author`), privileged MFA enforcement, billing-exempt policy for `admin`/`author`, and suspended/canceled account blocking on protected endpoints.
- Added `scripts/supabase-project-reachability-check.ps1` to verify Supabase project availability across Auth login, PostgREST (DB API), and Storage API, including safe normalization of escaped `.env` smoke-test passwords.
- Added `scripts/openai-account-check.ps1` to verify OpenAI readiness by validating API-key access (`/v1/models`) and confirming billing-enabled request execution via a minimal chat completion call.
- Auth planning language normalized to include both email/password and OAuth SSO (Google/Apple) for MVP.
- Database schema clarified for user isolation scope (`user_id` required on user-scoped tables) and extended with `qa_interactions` as canonical source for Q/A export history.
- Trial lifecycle removed from planning/contracts by product decision; billing model is now strictly `free/premium` plus coupon/discount management.

---

## Changelog Update Rule

- Update this file whenever a change is user-visible or developer-relevant.
- Prefer updating `Unreleased` in the same PR/iteration as the change.
- If a changelog update is skipped, document the reason in the PR notes.



















