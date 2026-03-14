# Personal AI Assistant - Execution TODO (World-Class MVP)

This TODO is designed for real execution: atomic tasks, clear dependencies, integrated quality.

## Agent Operating Contract (non-negotiable)
- Work only on the first incomplete task in this file unless the user explicitly overrides.
- Use document routing from `docs/AGENTS.md` before making implementation decisions.
- If documents conflict, stop and ask the user before coding.
- Do not modify architecture, memory model, or security rules unless explicitly requested.
- Run end-of-milestone mini-audit before starting the next milestone.
- Treat missing prerequisites as blockers, not assumptions.
- Enforce full-document alignment on every change: update all impacted files (`PROJECT_CONTEXT.md`, `docs/`, `specs/`, `TODO.md`) in the same iteration.
- Never leave contradictions across documents; if alignment cannot be completed, stop and report blocker explicitly.
- Follow `docs/coding-standards.md` for all implementation and refactoring decisions.
- Keep `CHANGELOG.md` updated for relevant changes in the same iteration whenever feasible.

## Execution protocol (always-on)
- Follow milestone order unless explicitly overridden.
- Complete only the first incomplete item of the active milestone.
- Respect strict dependency order: backend + DB first, then AI pipeline and API contracts, then auth enforcement, then user-facing features.
- Use a Docker-first development strategy: run backend + database + storage locally in containers whenever feasible.
- Use external SaaS only where local parity is not practical (`OpenAI`, `Supabase`, later `Stripe`).
- Keep security controls enabled by default.
- Never introduce arbitrary command execution.
- Keep architecture modular; avoid monolithic files.
- Keep docs and implementation aligned in the same milestone.

## Global quality gates (single Definition of Done)
- [x] `docker compose config` passes.
- [x] Required services are `healthy` in `docker compose ps`.
- [x] Lint/tests/build pass for touched components.
- [x] At least one runtime smoke check passes (not only unit tests).
- [x] `.env.example`, compose config, and setup docs are aligned.
- [x] `CHANGELOG.md` is updated for relevant behavior/contract/process changes.
- [x] Every feature includes automated tests (unit + integration where needed).
- [x] No merge without green CI.
- [x] Structured logging + metrics + consistent error handling are active.
- [x] LLMOps dashboards and alert thresholds are aligned with `docs/llmops-dashboard-spec.md`.
- [x] Product analytics events follow `docs/product-analytics.md` schema and naming contract.
- [x] Backend logs are production-grade (structured JSON, correlation IDs, user context, stack traces, secret/PII redaction).
- [x] Security by default: valid auth, strict `user_id` isolation, no data leak.
- [x] For B2B tenant changes: strict `tenant_id` + `user_id` isolation rules are enforced per `docs/multi-tenancy.md`.
- [x] For auth changes: Supabase Auth login/token -> protected API call succeeds (`401` without token, `200` with valid token).
- [x] For auth changes: email/password login flow succeeds.
<!-- - [ ] For auth changes: SSO login flow succeeds for enabled providers (MVP: Google, Apple). -->
- [x] For auth changes: 2FA policy is enforced (`admin`/`author` must have 2FA enabled; `user` can enable 2FA optionally).
- [x] For API changes: `specs/api.yaml` is updated and consistent with implementation.
- [x] For API changes: FastAPI OpenAPI/Swagger docs remain accurate and complete.
- [x] For API lifecycle changes: backward compatibility rules in `docs/api-compatibility.md` are respected.
- [x] For i18n changes: `preferred_language` behavior is consistent across backend responses and Flutter UI labels.
- [x] API errors follow `docs/error-model.md` (schema, codes, HTTP mapping).
- [x] For memory-ingestion changes: `input -> extraction -> clarification (if needed) -> explicit confirm -> DB persistence` is verified end-to-end.
- [x] For question-engine changes: database-first path is verified (`query/aggregation in backend`, LLM used only for final phrasing).
- [x] For question-engine changes: behavior is aligned with `docs/query-contract.md`.
- [x] For semantic caching changes: behavior is aligned with `docs/semantic-caching.md`.
- [x] For AI UX changes: behavior is aligned with `docs/ai-ux-contract.md`.
- [x] For attachment changes: `receipt photo upload -> OCR extraction -> memory proposal -> explicit confirm -> persistence + authorized signed URL access` is verified.
- [x] For attachment changes: lifecycle states are verified end-to-end (`uploaded -> ocr_processing -> proposal_ready -> confirmed -> persisted` and failure branches).
- [x] For AI-related changes: token usage/cost logging remains active and visible in metrics.
- [x] For AI model/prompt changes: `docs/model-registry.md` is updated with active version mapping and rollback entry.
- [x] AI cost controls stay active: token budget, per-user cost visibility, spike alerting.
- [x] For frontend-browser calls (if present): protected endpoint CORS preflight (`OPTIONS`) succeeds.
- [x] Flutter UI uses reusable components and centralized theme tokens (no scattered hardcoded styles/colors).
- [x] Test scope is aligned with `docs/testing-strategy.md` for touched components.
- [x] Environment/config choices are aligned with `docs/environment-matrix.md`.
- [x] Security-sensitive changes are checked against `docs/security-threat-model.md`.
- [x] AI-input/output safety changes are aligned with `docs/content-moderation.md` and `docs/data-sanitization.md`.
- [x] Auth/role/permission changes are aligned with `docs/rbac-matrix.md`.

---

## Founder/Developer Prerequisites (accounts and access)

Complete this checklist before implementation to avoid setup blockers.

### Hard blockers before Sprint 1 start
- [ ] Supabase project is created and reachable (Auth + Postgres + Storage).
- [ ] OpenAI API key is valid and billing is enabled.
- [ ] `.env.example` values are complete for local boot.
- [ ] At least one owner and one backup owner are assigned in Day 0 Operational Registry.
- [ ] MFA is enabled on Git hosting, OpenAI, Supabase, and Stripe accounts.

### Required accounts (MVP)
- [ ] Git hosting account and repository access configured.
- [ ] OpenAI account with active API billing and API key.
- [ ] Supabase project created (Auth + Postgres + Storage enabled).
- [ ] PostgreSQL environment ready:
- [ ] Supabase local Postgres (via Supabase CLI/Docker) for development
- [ ] Supabase managed Postgres for staging/prod
- [ ] Object storage ready:
- [ ] Supabase local Storage (via Supabase CLI/Docker) for development
- [ ] Supabase Storage buckets configured for staging/prod
- [ ] Stripe account with test mode enabled (for billing phase).

### Recommended accounts (to reduce risk)
- [ ] Error monitoring account (e.g., Sentry or equivalent).
- [ ] Uptime/observability platform account (metrics, dashboards, alerts).
- [ ] CI platform connected to repository (GitHub Actions or equivalent).
- [ ] Secret manager available for staging/production credentials.
- [ ] Transactional email provider account (provider TBD; decision tracked separately).

### Access and security setup
- [ ] Enable MFA on all critical services (Git, OpenAI, auth provider, cloud, Stripe).
- [ ] Create separate credentials for `dev`, `staging`, and `prod`.
- [ ] Restrict API keys by environment and rotate keys policy documented.
- [ ] Store secrets only in env/secret manager, never in source control.
- [ ] Define team access roles (author/admin/developer/read-only).

### Environment readiness checks
- [ ] `.env.example` completed with all required variables for local startup.
- [ ] Supabase Auth test users and token validation path verified.
- [ ] OpenAI key validated with a minimal API test call.
- [ ] Postgres connection, migration run, and rollback test completed.
- [ ] Object storage upload/download test completed.
- [ ] Stripe test webhook delivery validated locally.

### Budget and limits safeguards
- [ ] Set monthly spending cap for OpenAI usage.
- [ ] Configure usage alerts for AI spend spikes.
- [ ] Set free-tier limits to prevent runaway costs during tests.
- [ ] Define ownership of billing notifications and incident escalation.

### Legal and operational minimum
- [ ] Draft privacy policy baseline (data stored, retention, deletion process).
- [ ] Draft terms baseline for MVP users.
- [ ] Define support contact and incident response owner.

### Day 0 (owner checklist, 2-4 hours)
- [ ] Create/verify accounts: OpenAI, Supabase, Stripe (test mode).
- [ ] Enable MFA everywhere and store recovery codes securely.
- [ ] Generate dev-only keys/secrets and place them in local secret storage.
- [ ] Set OpenAI budget cap and spend alerts.
- [ ] Run minimal connectivity checks (OpenAI test call, DB connect, storage upload).
- [ ] Mark this section done only when no external dependency remains blocked.

### Day 1 (project readiness, 2-4 hours)
- [ ] Confirm local toolchain: Docker, Python, package manager, Flutter SDK.
- [ ] Validate `docker compose config` and ensure services become healthy.
- [ ] Ensure local Docker stack includes at minimum: `backend` + Supabase local stack (`auth`, `postgres+pgvector`, `storage`).
- [ ] Verify `.env.example` completeness against actual runtime needs.
- [ ] Execute one full smoke path: backend boot -> health endpoints -> DB readiness.
- [ ] Record all setup commands in `README.md` so setup is reproducible.

### Day 0 Operational Registry (fill this once, then maintain)

Use this as your single source of truth for external dependencies and ownership.

| Service | Purpose | Environment(s) | Console URL | Secret/Key Name | Owner | Backup Owner | Status | Last Verified | Notes |
|---|---|---|---|---|---|---|---|---|---|
| OpenAI | LLM + Whisper APIs | dev/staging/prod | TODO | TODO | TODO | TODO | planned | TODO | Billing enabled + spend cap set |
| Supabase (managed) | Auth + Postgres + Storage | staging/prod | TODO | TODO | TODO | TODO | planned | TODO | JWT settings, backups, storage buckets configured |
| Supabase (local CLI/Docker) | Local Auth + Postgres + Storage | dev | local | n/a | TODO | TODO | planned | TODO | Local parity with managed project verified |
| Stripe | Billing + subscriptions | staging/prod | TODO | TODO | TODO | TODO | planned | TODO | Test mode and webhooks verified |
| Email Provider (TBD) | Transactional notifications | staging/prod | TODO | TODO | TODO | TODO | planned | TODO | Domain authentication + delivery monitoring |
| CI Platform | Build/test automation | dev/staging/prod | TODO | TODO | TODO | TODO | planned | TODO | Required checks enabled |
| Monitoring/Alerts | Uptime + errors + cost alerts | staging/prod | TODO | TODO | TODO | TODO | planned | TODO | On-call notification path set |

### Day 0 Credentials and Policy Checklist
- [ ] Key naming convention defined (example: `APP_<SERVICE>_<ENV>_<PURPOSE>`).
- [ ] Secret rotation cadence defined (recommended: every 90 days).
- [ ] Access revocation process defined for team offboarding.
- [ ] Incident contact list documented (primary + backup).
- [ ] Billing alert thresholds defined (warning/critical).

---

## P0 - Product Lock and Setup (blocking)

- [ ] Confirm final stack: Flutter, FastAPI, Supabase (Auth + Postgres + Storage), pgvector, Whisper, Stripe.
- [ ] Lock MVP language matrix and fallback policy (`en`, `it`, `de`; default fallback `en`).
- [ ] Lock authentication policy for MVP: Supabase Auth with email/password + OAuth SSO (Google/Apple) + 2FA model (mandatory for `admin`/`author`).
- [ ] Freeze MVP scope and non-goals in one source of truth document.
- [ ] Define initial feature-flag governance model (naming, ownership, expiry, kill-switch requirements).
- [ ] Resolve and lock canonical memory taxonomy and fields across all specs (`expense_event/inventory_event/loan_event/note/document` + semantic fields).
- [ ] Assign owners for governance docs (`testing-strategy`, `environment-matrix`, `error-model`, `operations-runbook`, `security-threat-model`).
- [ ] Define review cadence for governance docs (recommended: at each milestone mini-audit).
- [ ] Define MVP KPIs:
- [ ] `memory_save_success_rate >= 95%`
- [ ] `avg_question_latency_p95 <= 3s` (text query only)
- [ ] `voice_pipeline_latency_p95 <= 12s`
- [ ] `extraction_confirmation_rate >= 85%`
- [ ] `time_to_first_successful_memory <= 2 minutes` (new user onboarding success)
- [ ] Define `dev/staging/prod` environments and required variables.
- [ ] Set up repository quality gates: lint, format, type check, test.
- [ ] Add pre-commit hooks for fast local checks (format/lint/type-check + targeted tests).
- [ ] Define branding baseline for MVP: app name `Personal AI Assistant` + placeholder logo asset usage.
- [ ] Set up baseline CI (build + test + lightweight security scan).

---

## P1 - Backend Foundation

- [ ] Create modular FastAPI structure (`api`, `services`, `repositories`, `domain`).
- [ ] Implement typed config management (env validation).
- [ ] Set up JSON logging with `request_id` and `user_id` (when available).
- [ ] Add request tracing (`trace_id`) to support cross-service debugging.
- [ ] Add error-handling middleware with standard error codes.
- [ ] Define asynchronous job boundary (API request path vs background worker path).
- [ ] Health endpoints:
- [ ] `GET /health/live`
- [ ] `GET /health/ready`
- [ ] Backend Dockerfile + local `docker-compose` with Postgres.
- [ ] Backend startup smoke test + health checks.

---

## P2 - Database and Migrations

- [ ] Set up migrations (Alembic or equivalent).
- [ ] Enable `pgvector` extension.
- [ ] Create tables: `users`, `memories`, `memory_versions`, `attachments`, `embeddings`, `qa_interactions`.
- [ ] Add user billing-policy fields (`role`, `subscription_plan`, `billing_exempt`) with constraints.
- [ ] Define FKs, constraints, and indexes on critical query fields (`user_id`, `created_at`, `memory_type`).
- [ ] Implement memory versioning strategy (`memory_versions` append-only).
- [ ] Enforce per-user isolation policy across all repository queries.
- [ ] Prepare tenant-ready schema strategy (`tenant_id` support) for B2B isolation path.
- [ ] Add idempotency strategy for write endpoints to prevent duplicate memory creation on retries.
- [ ] Add soft-delete + audit trail strategy for sensitive memory operations (update/delete).
- [ ] Add `structured_data_schema_version` support for forward-compatible payload evolution.
- [ ] Create realistic local seed dataset for tests.
- [ ] Test migration up/down in CI.

---

## P3 - AI Memory Ingestion Pipeline

- [ ] Endpoint `POST /api/v1/voice/memory` with robust audio upload handling.
- [ ] Whisper integration with timeout and controlled retry.
- [ ] Versioned extraction prompt (`specs/memory-extraction.md`).
- [ ] Register extraction/clarification model + prompt versions in `docs/model-registry.md`.
- [ ] `memory_type` classification (`expense_event`, `inventory_event`, `loan_event`, `note`, `document`).
- [ ] Enforce required fields per `memory_type` before persistence (`required_by_type` contract).
- [ ] Typed + semantic field extraction (`who/what/where/when/why/how`).
- [ ] Apply default `when = current timestamp` when user does not provide explicit date/time.
- [ ] Normalize relative time expressions (`today`, `yesterday`, etc.) to absolute date/time before confirmation and save.
- [ ] Clarification engine for missing fields (configurable max turns).
- [ ] Confirmation contract: `confirm/modify/cancel` before persistence.
- [ ] Persist memory only after explicit confirmation.
- [ ] Move expensive AI tasks (transcription/embeddings when applicable) to background jobs where latency requires it.
- [ ] Generate embeddings only for confirmed create/update events.
- [ ] Capture per-request AI telemetry (model, token usage, estimated cost, latency).
- [ ] Add strict anti-hallucination guardrails for extraction output schema.
- [ ] Apply input moderation and sensitive-data sanitization before LLM extraction call.
- [ ] End-to-end test: voice -> extraction -> confirmation -> storage.

---

## P4 - API Endpoints and Contracts

- [ ] Implement and wire endpoint handlers:
- [ ] `POST /api/v1/voice/memory`
- [ ] `POST /api/v1/voice/question`
- [ ] `POST /api/v1/question`
- [ ] `POST /api/v1/question/stream` (SSE streaming answer with chunk/done events)
- [ ] `POST /api/v1/feedback/answers` (like/dislike answer feedback with optional reason/comment)
- [ ] `POST /api/v1/memory`
- [ ] `GET /api/v1/memories`
- [ ] `DELETE /api/v1/memory/{id}`
- [ ] `POST /api/v1/attachments`
- [ ] `GET /api/v1/dashboard`
- [ ] `GET /api/v1/admin/users` (admin/author)
- [ ] `PATCH /api/v1/admin/users/{id}/status` (admin/author: suspend/reactivate/cancel)
- [ ] `PATCH /api/v1/author/users/{id}/role` (author only: `user` <-> `admin`)
- [ ] `GET /api/v1/author/dashboard` (author only global supervision)
- [ ] `GET /api/v1/me/settings`
- [ ] `PATCH /api/v1/me/settings/profile` (includes `preferred_language`)
- [ ] `PATCH /api/v1/me/settings/security` (password/email/2FA security flow trigger)
- [ ] `PATCH /api/v1/me/settings/notifications` (notification channels preferences)
- [ ] `GET /api/v1/me/settings/payment-methods` (masked cards list)
- [ ] `POST /api/v1/me/settings/payment-methods/setup-intent` (provider setup intent for add/update)
- [ ] `POST /api/v1/me/settings/payment-methods/{id}/default` (set default payment method)
- [ ] `DELETE /api/v1/me/settings/payment-methods/{id}` (remove payment method)
- [ ] `GET /api/v1/notifications` (in-app notifications feed)
- [ ] `POST /api/v1/notifications/{id}/read` (mark notification as read)
- [ ] `POST /api/v1/billing/subscription/change-plan` (`free` <-> `premium`)
- [ ] `POST /api/v1/billing/subscription/cancel-preview` (churn prevention preview)
- [ ] `POST /api/v1/billing/subscription/cancel` (cancel with mandatory reason)
- [ ] `GET /api/v1/me/retention/status` (churn risk + recommended retention actions)
- [ ] `POST /api/v1/billing/coupons/apply` (coupon apply for eligible users)
- [ ] `POST /api/v1/me/data-export` (start export job: `json/csv/pdf`)
- [ ] `GET /api/v1/me/data-export/{job_id}` (export status + signed URL)
- [ ] Ensure request/response schemas align with `specs/api.yaml`.
- [ ] Define explicit API contract from receipt attachment OCR output to memory proposal creation (no implicit hidden transition).
- [ ] Return `422 memory.missing_required_fields` when save is attempted with incomplete required fields.
- [ ] Add API contract tests for core success/error responses.
- [ ] Add streaming API tests (`chunk` ordering, terminal `done` event, fallback on stream failure).
- [ ] Add compatibility tests for active and previous supported client contract.
- [ ] Add privileged-policy tests (`last active author protection`, `self-role-change forbidden`, `billing.plan_locked_by_role`).
- [ ] Add consistent error model and status code mapping.

---

## P5 - Auth and Access Control

- [ ] Integrate Supabase Auth JWT validation in backend.
- [ ] Enable email/password auth in Supabase Auth for MVP.
- [ ] Enable SSO providers in Supabase Auth for MVP (`Google`, `Apple`).
- [ ] Add mandatory auth middleware for protected endpoints.
- [ ] Auto-provision user on first access.
- [ ] Map token claims -> internal `user_id`.
- [ ] Implement 2FA/TOTP enrollment and verification flow in security settings.
- [ ] Enforce 2FA policy by role:
- [ ] `admin` and `author` must have `mfa_enabled = true`
- [ ] `user` can opt in/out unless tightened later by policy change
- [ ] Add role-based access control (`user`, `admin`, `author`) and enforce on privileged endpoints.
- [ ] Add tenant-aware authorization guardrails for future B2B mode (`tenant_id` context propagation + checks).
- [ ] Add user account status control (`active`, `suspended`, `canceled`) and block access when suspended/canceled.
- [ ] Enforce author safety invariants:
- [ ] author cannot change own role
- [ ] author cannot suspend/cancel own account
- [ ] system must always keep at least one active author
- [ ] Negative auth tests:
- [ ] missing token
- [ ] expired token
- [ ] missing/invalid 2FA code on sensitive security action
- [ ] admin/author with 2FA disabled blocked from privileged access until remediation
- [ ] valid token but cross-user resource access
- [ ] suspended user access blocked
- [ ] canceled user access blocked
- [ ] non-admin access blocked on admin routes
- [ ] non-author access blocked on author routes
- [ ] admin cannot change roles (author-only role transition endpoint)
- [ ] role change to `admin`/`author` auto-enforces `premium` + billing exemption

---

## P6 - Query Engine (Database-First)

- [ ] Align question behaviors and edge cases with `docs/query-contract.md`.
- [ ] Equivalent text-query endpoint for testing and fallback.
- [ ] Intent detection oriented to SQL queries/aggregations.
- [ ] Enforce strict rule: calculations in backend, never in LLM.
- [ ] Implement deterministic rule for "latest/last": `ORDER BY when DESC LIMIT 1`.
- [ ] Implement ambiguity handling with clarification question before final answer.
- [ ] Implement no-result fallback response (no fabrication).
- [ ] Define and enforce multi-currency policy (no silent conversion; explicit aggregation rules by currency).
- [ ] Core aggregate queries:
- [ ] expenses by period/category/object
- [ ] loan balances (who owes what)
- [ ] inventory state from events
- [ ] Semantic retrieval with pgvector for open-ended questions.
- [ ] Implement semantic answer cache with user-scoped keying and similarity threshold.
- [ ] Add semantic cache invalidation rules on memory create/update/delete.
- [ ] Minimal context builder to reduce token usage.
- [ ] Natural-language response generation from structured backend result.
- [ ] Add pre-generation and post-generation moderation checks on question flow.
- [ ] Enforce retrieval priority: structured SQL first, semantic vector fallback.
- [ ] Persist question-path AI telemetry for per-user/per-feature cost visibility.
- [ ] Add answer confidence/provenance payload (source memory IDs used for response).
- [ ] Regression tests for key questions from `README.md`.

---

## P7 - Flutter Mobile App

- [ ] Bootstrap Flutter app with clean architecture (state management decided and fixed).
- [ ] Login/logout with Supabase Auth.
- [ ] First-run onboarding focused on fast first value (first memory + first question).
- [ ] Onboarding step 1: welcome + value proposition + privacy short notice.
- [ ] Onboarding step 2: language selection (`en`/`it`/`de`) and persistence to `preferred_language`.
- [ ] Onboarding step 3: permission guidance and request flow (microphone required; camera optional for receipt flow).
- [ ] Onboarding step 4: guided first memory capture with explicit confirmation (`Confirm/Modify/Cancel`).
- [ ] Onboarding step 5: guided first question flow with "Why this answer" disclosure.
- [ ] Onboarding completion state persisted (`onboarding_completed_at`) to avoid repeating full wizard.
- [ ] Add skip/resume onboarding behavior with deterministic resume point.
- [ ] Add onboarding fallback path when permission is denied (clear CTA to retry/open OS settings).
- [ ] Build chat-style memory capture screen with bottom composer (`text`, `mic`, `send`, `attachment`).
- [ ] Implement AI chat surface states per UX contract (`idle`, `processing`, `needs_clarification`, `ready_to_confirm`, `saved`, `failed`).
- [ ] Build reusable Flutter component library for common UI patterns (buttons, inputs, cards, status blocks).
- [ ] Centralize Flutter style tokens (colors, typography, spacing) and enforce usage across all screens.
- [ ] Implement Flutter i18n architecture (arb-based keys, locale resolution, fallback to English).
- [ ] Add architecture lint/static rules to block business logic inside Flutter widgets/screens.
- [ ] Attachment button UX: support both `Take Photo` and `Choose from Gallery` for receipt photos.
- [ ] Push-to-talk memory capture.
- [ ] Memory confirmation flow with `Confirm / Modify / Cancel` only.
- [ ] Implement `Modify` as guided field editor by memory type.
- [ ] Ask Assistant (voice + text).
- [ ] Show absolute editable datetime in confirmation (`YYYY-MM-DD HH:mm`).
- [ ] Implement one-question-per-turn clarification UX.
- [ ] Memory timeline with basic filters.
- [ ] MVP dashboard screen.
- [ ] Build user `Settings` screen (profile, security, subscription).
- [ ] Add language selection in Settings (`English`, `Italian`, `German`) bound to backend `preferred_language`.
- [ ] Add auth settings UX for SSO visibility (linked provider) and 2FA management (enable/disable/verify).
- [ ] Add notification preferences UI in settings (in-app/push/email toggles).
- [ ] Add payment methods section in Settings (add card, set default, remove card, masked card display only).
- [ ] Build in-app notification center with unread/read state and deep links to related screens.
- [ ] Build admin `User Management` screen (list users, search/filter, suspend/reactivate/cancel).
- [ ] Build author `Supervision Dashboard` screen (global metrics + oversight panels).
- [ ] Build author role-management UI (promote/demote `user` <-> `admin`).
- [ ] User-friendly error handling (retry, offline state, timeout).
- [ ] Keep UI widgets thin; move business logic to dedicated services/controllers/state layer.
- [ ] Query answer UI: concise answer + expandable "Why this answer" panel (confidence + sources).
- [ ] Add streaming answer UI mode (typing effect with SSE chunks + graceful fallback to non-stream endpoint).
- [ ] Add answer feedback UI (`Like` / `Dislike`) with optional reason/comment capture.
- [ ] No-result UI: clear message + CTA to "Add Memory".
- [ ] Ensure AI microcopy/actions/error states follow `docs/ai-ux-contract.md`.
- [ ] Widget tests on critical flows.

---

## P8 - Dashboard and Insights

- [ ] Endpoint `GET /api/v1/dashboard` with core metrics.
- [ ] Endpoint `GET /api/v1/author/dashboard` with global supervision metrics (author only).
- [ ] MVP blocks:
- [ ] current-month expenses vs previous month
- [ ] latest memory events
- [ ] open loans
- [ ] summarized inventory state
- [ ] Dashboard caching (short TTL) to reduce cost.
- [ ] Numeric consistency tests: dashboard vs raw DB queries.

---

## P9 - Attachments

- [ ] Integrate Supabase Storage.
- [ ] Endpoint `POST /api/v1/attachments` with strict file type/size validation (receipt photos only).
- [ ] Link attachment <-> memory with user ownership checks.
- [ ] Introduce attachment lifecycle state machine (`uploaded`, `ocr_processing`, `proposal_ready`, `confirmed`, `persisted`, `failed`) with deterministic transitions.
- [ ] Run OCR on uploaded receipt photo and expose preview text for memory proposal flow.
- [ ] Normalize receipt photo before OCR (orientation/rotation, optional compression, quality guardrails).
- [ ] Parse and normalize OCR fields (amount/currency/date/vendor candidates) with explicit uncertainty flags.
- [ ] Ensure scan/upload alone never persists memory (confirm required).
- [ ] Temporary signed URLs for file access.
- [ ] Minimum support: receipt photo images only (`jpg`, `jpeg`, `png`, `webp`, `heic`).
- [ ] Explicitly reject `pdf` and every non-image content type on upload.
- [ ] Strip sensitive EXIF metadata before long-term storage.
- [ ] Add file hash-based dedup strategy to avoid duplicate OCR and duplicate attachment storage.
- [ ] Define orphan attachment policy (uploaded but never confirmed) with automatic cleanup job and retention window.
- [ ] Define delete semantics: memory deletion must enforce attachment deletion/retention policy consistently in DB and object storage.
- [ ] Basic malware scanning (if available in selected provider).
- [ ] Upload/download authorization tests.

---

## P10 - Monetization and Limits

- [ ] Integrate Stripe checkout + backend webhook handling.
- [ ] Implement `free` and `premium` plans in backend authorization logic.
- [ ] Integrate Stripe setup-intent flow for payment method onboarding/update.
- [ ] Enforce role-based plan lock: `admin`/`author` are always `premium` and billing-exempt.
- [ ] Enforce free plan limits:
- [ ] monthly memories
- [ ] monthly AI queries
- [ ] attachment storage
- [ ] Track per-user usage (monthly + cumulative).
- [ ] Apply per-user and per-endpoint rate limiting by subscription plan.
- [ ] Graceful degradation when limits are exceeded.
- [ ] Billing webhook and plan-switch tests.
- [ ] In-app subscription management UX for user (`upgrade`, `downgrade`, current plan visibility).
- [ ] In-app payment methods management UX for `user` role.
- [ ] Restrict subscription self-service to `user` role; `admin`/`author` plan changes follow role policy.
- [ ] Grace period and downgrade policy defined and enforced.
- [ ] Add cancellation retention flow (`cancel-preview`): reason capture, pause/downgrade alternatives, final cancel confirmation.
- [ ] Persist and analyze churn reasons to guide product/pricing improvements.
- [ ] Add proactive churn-risk scoring and trigger retention interventions before cancel intent.
- [ ] Implement coupon/discount logic (validity window, usage limits, anti-abuse controls).

---

## P10.5 - Transactional Notifications

- [ ] Define unified notification policy (event taxonomy, templates, localization, legal footer, channel routing rules).
- [ ] Add automatic notifications for security/account-critical events:
- [ ] email change requested/completed
- [ ] password change requested/completed
- [ ] account suspension/reactivation
- [ ] plan upgrade/downgrade and billing failures
- [ ] Integrate email delivery provider abstraction (provider `TBD`, to be selected separately).
- [ ] Integrate push delivery provider/service abstraction (FCM/APNs via provider adapter).
- [ ] Implement in-app notification persistence (`notifications` table/model) with read/unread lifecycle.
- [ ] Add push token registration/rotation/revocation flow per device session.
- [ ] Add notification delivery logs, retry, and dead-letter handling.
- [ ] Add user-level notification preferences and channel opt-in/opt-out enforcement.
- [ ] Add tests for notification triggers, per-channel routing, and failure behavior.

---

## P11 - AI Cost Control Optimization (mandatory before go-live)

- [ ] Validate and harden per-request tracking quality: model, input/output tokens, estimated cost.
- [ ] Internal dashboard for cost per user and per feature.
- [ ] Automatic alerts for daily cost spikes.
- [ ] Prompt budget with hard token cap.
- [ ] Cache low-risk repeated responses.
- [ ] Track semantic cache hit/miss ratio and latency/cost impact in LLMOps dashboards.
- [ ] Model routing policy (cost-efficient default, escalation for complex cases).
- [ ] Formalize per-use-case active model mapping and fallback chain in `docs/model-registry.md`.
- [ ] Add circuit breaker/fallback behavior for AI provider outages and elevated error rates.
- [ ] Load-test simulation to estimate monthly cost.
- [ ] Implement product analytics event pipeline (capture, validation, storage/export) aligned with `docs/product-analytics.md`.
- [ ] Track core funnels and KPI derivations from canonical events (first memory, first question, receipt flow).
- [ ] Implement required LLMOps dashboards and threshold alerts from `docs/llmops-dashboard-spec.md`.
- [ ] Validate critical alert-to-runbook mapping for LLM incidents in staging before prod.
- [ ] Add A/B framework support for AI prompt/model variants with guardrails and rollback criteria.

---

## P12 - Security, Privacy, Compliance

- [ ] Encryption in transit (TLS) and at rest (DB + object storage).
- [ ] Harden input validation (audio/file/json) and rate limiting.
- [ ] Audit logs for sensitive operations (delete, export, billing changes).
- [ ] User privacy functions:
- [ ] data export
- [ ] account and data deletion
- [ ] explicit data retention policy
- [ ] Data portability exports support `json`, `csv`, and `pdf` via asynchronous jobs.
- [ ] Implement automated data-lifecycle jobs for account closure (`canceled_pending_deletion -> deletion_completed`).
- [ ] Ensure deletion covers DB + storage + embeddings + caches with idempotent retries.
- [ ] Serious secret management (no secrets in repo/logs).
- [ ] Minimal threat model + OWASP API Top 10 checklist.
- [ ] Define GDPR-ready privacy baseline (consent, data export/delete SLA, retention policy enforcement).
- [ ] Lightweight pre-release security test (manual + automated tooling).
- [ ] Implement prompt sanitization/redaction layer before AI provider calls.
- [ ] Implement content moderation policy enforcement (`allow/warn/block/review`) with deterministic logging.

---

## P13 - Production Readiness and Launch

- [ ] Automated staging deployment.
- [ ] Deploy backend in cloud with minimum 2 instances for staging/prod.
- [ ] Configure managed load balancer with health-check routing (`/health/live`, `/health/ready`).
- [ ] Define and implement autoscaling policy (CPU/memory/latency thresholds + min/max replicas).
- [ ] Configure zero-downtime rollout strategy (rolling update or blue/green).
- [ ] Enforce edge timeout/rate-limit baseline at load balancer or API gateway layer.
- [ ] Automated post-deploy smoke tests.
- [ ] Full monitoring:
- [ ] uptime
- [ ] endpoint latency
- [ ] error rate
- [ ] job failure rate
- [ ] SLI dashboard with error budget burn rate for core user journeys.
- [ ] Automatic backups and tested restore procedure.
- [ ] Incident runbook (AI outage, DB outage, storage outage).
- [ ] Validate incident procedures against `docs/operations-runbook.md` with at least one tabletop simulation.
- [ ] Define SLOs and error budget policy for API and voice pipelines.
- [ ] Define and test backup/restore targets (`RPO`/`RTO`) with evidence.
- [ ] Feature flags for controlled rollout.
- [ ] Implement runtime feature-flag targeting (role/plan/app-version/percentage cohorts) without restart.
- [ ] Add kill-switch operational procedure for high-risk feature rollback.
- [ ] Define and publish client support matrix + API deprecation/sunset process.
- [ ] Private beta with weekly feedback loop.
- [ ] Signed go-live checklist.

---

## Continuous Quality Backlog (always active)

- [ ] API contract validation: `specs/api.yaml` vs implementation.
- [ ] Keep `CHANGELOG.md` updated for user-visible and developer-relevant changes.
- [ ] Add automated log schema contract tests for backend structured logs (required fields + redaction guarantees).
- [ ] Add automated analytics event schema tests for core events and event versioning compatibility.
- [ ] Realistic multilingual (EN/IT/DE) extraction and query test datasets.
- [ ] Prompt evaluation suite with precision/recall benchmarks.
- [ ] Hallucination and safety eval suite for ambiguous user questions.
- [ ] Performance budget and quarterly profiling.
- [ ] Truly tested multi-provider AI plan (not only abstract design).
- [ ] Planned technical debt reduction in every sprint.
- [ ] Record architecture-level tradeoffs as ADRs in `ADR/`.
- [ ] Maintain golden dataset + automated eval harness for extraction and question-answer regressions.

---

## Recommended MVP Milestones

- [ ] M1: P0-P3 complete (reliable foundations).
- [ ] M2: P4-P6 complete (API + auth + question engine end-to-end).
- [ ] M3: P7-P9 complete (mobile + dashboard + attachments).
- [ ] M4: P10-P13 complete (billing + optimization + security + production).

### Mandatory End-of-Milestone Mini-Audit
- [ ] Confirm implementation is aligned with `PROJECT_CONTEXT.md`, `docs/`, and `specs/`.
- [ ] Confirm no architecture decision was violated.
- [ ] Confirm security controls and strict `user_id` isolation are still enforced.
- [ ] Confirm touched API behavior matches `specs/api.yaml`.
- [ ] Document open gaps, risks, and blockers before starting the next milestone.

---

## Sprint 1 Execution Plan (5 working days)

Goal: deliver a production-grade backend foundation plus DB baseline (P0-P2 first slice).

### Day 1 - Foundation decisions and repo baseline
- [ ] Finalize P0 stack decisions in root docs already present (no architecture changes).
- [ ] Create implementation directories (`backend/`, `mobile/`, `infra/`, `scripts/`) following `PROJECT_FILE_STRUCTURE.md`.
- [ ] Initialize backend FastAPI app skeleton with modular packages.
- [ ] Add baseline tooling (`ruff`/`black`/`mypy` or equivalent) and test runner.
- [ ] Add `.env.example` with validated required vars for local startup.
- [ ] Deliverable: backend starts locally and `GET /health/live` returns `200`.

### Day 2 - Backend reliability baseline
- [ ] Implement typed settings loader with fail-fast env validation.
- [ ] Add structured JSON logging and request/trace IDs middleware.
- [ ] Add centralized error handling with stable API error format.
- [ ] Add readiness endpoint `GET /health/ready` checking DB connectivity contract (stub allowed if DB not wired yet).
- [ ] Add smoke test script for startup + health checks.
- [ ] Deliverable: startup smoke test green in local environment.

### Day 3 - Database and migrations baseline
- [ ] Add Supabase local stack (Auth + Postgres + Storage) in `docker-compose`/Supabase CLI setup.
- [ ] Set up migration framework and first migration baseline.
- [ ] Create core tables: `users`, `memories`, `memory_versions`, `attachments`, `embeddings`, `qa_interactions`.
- [ ] Add key indexes and constraints for `user_id`, `created_at`, `memory_type`.
- [ ] Add repository layer skeleton with mandatory per-user filtering contract.
- [ ] Deliverable: migrations run up/down cleanly and schema matches docs.

### Day 4 - Data access and robustness baseline
- [ ] Add DB repository patterns with strict `user_id` scoping hooks.
- [ ] Add idempotency key strategy draft for write endpoints.
- [ ] Add migration + data integrity smoke checks.
- [ ] Add basic rate-limit strategy placeholder for API safety.
- [ ] Add security headers/CORS baseline for expected client calls.
- [ ] Deliverable: DB access robustness checks validated end-to-end.

### Day 5 - Quality closure and CI
- [ ] Wire CI pipeline for lint + type-check + tests + migration check.
- [ ] Ensure `docker compose config` and service health checks pass.
- [ ] Ensure API spec sync workflow exists for touched endpoints.
- [ ] Add short runbook in `README.md` for local setup, test, and smoke flow.
- [ ] Sprint demo checklist: health, migration, data integrity, logging/tracing evidence.
- [ ] Deliverable: Sprint 1 release tag candidate ready for M1 continuation.

### Sprint 1 Exit Criteria
- [ ] All Day 1-5 deliverables completed.
- [ ] Global quality gates satisfied for touched components.
- [ ] No open P0/P1/P2 blocker preventing P3 start.

---

## TODO Maturity Checklist (what "perfect" means)

- [ ] Every task has a clear outcome that can be verified objectively.
- [ ] Every critical dependency appears before dependent tasks.
- [ ] Every external service has account + key + budget + alert readiness.
- [ ] Every milestone has at least one end-to-end smoke scenario.
- [ ] Security/privacy/cost controls are present both early and before launch.
- [ ] The first 7 working days can be executed without asking "what next?".
