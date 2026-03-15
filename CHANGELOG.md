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
- Added `KEY_NAMING_CONVENTION.md` with canonical secret/key naming pattern `APP_<SERVICE>_<ENV>_<PURPOSE>`, enforcement rules, and environment-specific examples.
- Added `SECRET_ROTATION_CADENCE.md` defining 90-day secret rotation baseline, minimum rotation procedure, emergency rotation trigger, and ownership model.
- Added `ACCESS_REVOCATION_OFFBOARDING.md` with team offboarding access-revocation checklist, SLA, validation steps, and audit-trail requirements.
- Added `INCIDENT_CONTACT_LIST.md` documenting primary and backup incident contacts plus escalation usage rules.
- Added `BILLING_ALERT_THRESHOLDS.md` documenting warning/critical billing alert thresholds and verification steps aligned with LLMOps runtime/test coverage.
- Added `FINAL_STACK_CONFIRMATION.md` to record the confirmed MVP stack baseline and source references.
- Added `MVP_LANGUAGE_MATRIX_LOCK.md` to formally lock MVP supported locales (`en`, `it`, `de`) and fallback policy (`en`).
- Added `MVP_AUTH_POLICY_LOCK.md` to formally lock MVP authentication policy (Supabase Auth, email/password + Google/Apple SSO, mandatory 2FA for `admin`/`author`).
- Added `MVP_SCOPE_SOURCE_OF_TRUTH.md` as the single source of truth for MVP in-scope capabilities and explicit non-goals.
- Added `FEATURE_FLAG_GOVERNANCE_BASELINE.md` defining initial feature-flag governance (naming, ownership, expiry, kill-switch, required metadata).
- Added `CANONICAL_MEMORY_TAXONOMY_LOCK.md` locking canonical memory types and semantic fields with cross-reference to API and extraction contracts.
- Added `GOVERNANCE_DOC_OWNERS.md` assigning primary/backup owners for governance documents (`testing-strategy`, `environment-matrix`, `error-model`, `operations-runbook`, `security-threat-model`).
- Added `GOVERNANCE_REVIEW_CADENCE.md` defining mandatory governance-doc review cadence at milestone mini-audits and additional review triggers.
- Added `MVP_KPI_BASELINE.md` locking initial MVP KPI targets and measurement/review rules.
- Added `ENVIRONMENT_REQUIREMENTS_BASELINE.md` defining `dev/staging/prod` baseline environments and required variable groups.
- Added `BRANDING_BASELINE.md` and placeholder logo asset `mobile/assets/branding/placeholder_logo.svg` with Flutter asset wiring in `mobile/pubspec.yaml`.
- Added repository quality-gate scripts: `scripts/lint-check.ps1`, `scripts/type-check.ps1`, `scripts/test-check.ps1`, `scripts/targeted-tests-check.ps1`, and `scripts/lightweight-security-scan.ps1`.
- Added `.pre-commit-config.yaml` with local hooks for `format`, `lint`, `type-check`, and targeted tests.
- Added backend modular package scaffolding for `repositories` and `domain` (`backend/app/repositories`, `backend/app/domain`) plus `backend/tests/test_backend_structure.py` to validate required FastAPI package layout.
- Added typed backend config loader `backend/app/core/settings.py` with fail-fast environment validation (`APP_ENV`, `LOG_LEVEL`, integer budget/port parsing, CORS origins parsing) and centralized settings access via `get_settings()`.
- Added `backend/tests/test_settings_validation.py` covering valid typed config parsing and invalid env failure modes.
- Added `backend/tests/test_logging_context_fields.py` to verify structured JSON logs always include context fields (`request_id`, `trace_id`, `user_id`, `tenant_id`) and default user placeholder behavior when unauthenticated.
- Extended `backend/tests/test_runtime_integration.py` with request-tracing checks to verify `x-trace-id` propagation and deterministic fallback to `x-request-id` when trace header is missing.
- Added `ErrorHandlingMiddleware` in `backend/app/core/middleware.py` and wired it in `backend/app/main.py` to standardize API error handling in middleware (`AppError`, validation, HTTP exceptions, unexpected failures) with stable error-code mapping.
- Added `backend/tests/test_error_handling_middleware.py` to verify middleware registration and standardized validation error code behavior.
- Added asynchronous job-boundary baseline in `ASYNC_JOB_BOUNDARY_BASELINE.md` and code source-of-truth mapping in `backend/app/domain/async_job_boundary.py` (`request_path` vs `background_worker` execution model).
- Added `backend/tests/test_async_job_boundary.py` to validate boundary-map uniqueness and expected execution-mode classification.
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
- Implemented and wired `GET /api/v1/dashboard` with authenticated user/tenant-scoped metrics (`total_memories`, `memories_by_type`, `latest_memory_events`) via dedicated route/service modules, added endpoint/OpenAPI regression tests, and marked the P4 dashboard endpoint task completed in `TODO.md`.
- Marked P4 endpoint task `POST /api/v1/attachments` as completed in `TODO.md` after validating receipt-photo upload contract, OCR proposal response, and OpenAPI exposure with green attachment E2E tests.
- Implemented and wired `DELETE /api/v1/memory/{id}` with user+tenant-scoped soft-delete behavior, `404 memory.not_found` for missing/foreign records, and contract response `{ \"deleted\": true }`.
- Added delete-path repository support (`soft_delete_memory_for_user`) and typed API response model (`DeleteMemoryResponse`).
- Added endpoint regression coverage in `backend/tests/test_memory_delete_endpoint.py` (success, not-found, cross-user isolation) and extended OpenAPI docs assertions for delete-memory route.
- Marked P4 endpoint task `DELETE /api/v1/memory/{id}` as completed in `TODO.md`.
- Marked P4 endpoint task `GET /api/v1/memories` as completed in `TODO.md` after validating authenticated user/tenant isolation behavior and OpenAPI contract with runtime tests.
- Marked P4 endpoint task `POST /api/v1/memory` as completed in `TODO.md` after validating confirmation gate, required-fields contract, persistence flow, and OpenAPI exposure with green regression tests.
- Implemented and wired `POST /api/v1/feedback/answers` with typed request validation (`answer_id`, `sentiment`, optional `reason/comment`), authenticated user scoping, and accepted-response contract (`{\"accepted\": true}`).
- Added modular feedback handling via `backend/app/services/answer_feedback.py` and operational analytics event emission (`answer_feedback_submitted`).
- Added endpoint regression coverage in `backend/tests/test_feedback_endpoint.py` (success, auth required, invalid sentiment) and OpenAPI contract assertion for feedback route.
- Marked P4 endpoint task `POST /api/v1/feedback/answers` as completed in `TODO.md`.
- Implemented and wired `POST /api/v1/question/stream` SSE endpoint with ordered `chunk` events and terminal `done` event payload (`confidence`, `source_memory_ids`), reusing database-first question flow and safety checks.
- Added streaming fallback behavior (`503 ai.provider_unavailable`) when stream is explicitly disabled via request header for client fallback handling.
- Added streaming regression tests in `backend/tests/test_question_streaming.py` and extended OpenAPI assertions to cover `/api/v1/question/stream`.
- Marked P4 endpoint task `POST /api/v1/question/stream` as completed in `TODO.md`.
- Marked P4 endpoint task `POST /api/v1/question` as completed in `TODO.md` after validating database-first behavior, moderation/sanitization enforcement, OpenAPI exposure, and AI telemetry/cost metrics with green regression suites.
- Implemented and wired `POST /api/v1/voice/question` with audio upload validation, Whisper transcription, pre-input moderation/sanitization, database-first answer flow reuse, and post-output safety enforcement.
- Added regression coverage for voice-question path in `backend/tests/test_voice_question_endpoint.py` (success, moderation block, unsupported audio type) and extended OpenAPI docs checks for `/api/v1/voice/question`.
- Marked P4 endpoint task `POST /api/v1/voice/question` as completed in `TODO.md`.
- Marked P4 endpoint task `POST /api/v1/voice/memory` as completed in `TODO.md` after validating router wiring, OpenAPI exposure, upload-validation behavior, and ingestion E2E flow (`test_openapi_docs`, `test_voice_memory_upload_validation`, `test_memory_ingestion_e2e` all green).
- Marked P3 task `End-to-end test: voice -> extraction -> confirmation -> storage` as completed in `TODO.md` after validating `backend/tests/test_memory_ingestion_e2e.py` green (`voice proposal -> confirmation gate -> persisted memory retrieval`).
- Completed P3 safety gate for memory extraction flow by enforcing input moderation and sensitive-data sanitization before extraction proposal generation in `POST /api/v1/voice/memory` and attachment OCR proposal path.
- Extended AI safety regression coverage with voice-memory tests that verify moderation blocking (`moderation.blocked_content`) and transcript redaction (`[REDACTED_EMAIL_1]`) before extraction.
- Marked P3 task `Apply input moderation and sensitive-data sanitization before LLM extraction call` as completed in `TODO.md`.
- Added strict extraction-schema anti-hallucination guardrails in memory ingestion: only allowed fields per `memory_type` are accepted, unsupported keys are dropped, and critical values are normalized/validated (numeric amounts/quantities, action enums, allowed currencies, bounded strings).
- Applied guardrails before confirmation proposal generation to keep extraction payload deterministic and schema-safe.
- Added guardrail-focused regression tests for unknown-field dropping, invalid value rejection, and proposal-level guardrail application.
- Marked P3 task `Add strict anti-hallucination guardrails for extraction output schema` as completed in `TODO.md`.
- Extended per-request AI telemetry to include latency (`latency_ms`) in usage logs and Prometheus metrics (`llmops_ai_latency_ms_total`, `llmops_ai_latency_ms_last`) while preserving existing model/token/cost dimensions.
- Wired latency capture into memory extraction (`POST /api/v1/voice/memory`), answer generation (`POST /api/v1/question`), and receipt OCR extraction (`POST /api/v1/attachments`) telemetry paths.
- Marked P3 task `Capture per-request AI telemetry (model, token usage, estimated cost, latency)` as completed in `TODO.md`.
- Added embedding generation on confirmed memory persistence (`POST /api/v1/memory`) and ensured embeddings are not generated when confirmation is missing or when save is replayed via idempotency key.
- Added in-memory embedding repository/service baseline and contract tests for confirmed-save generation, unconfirmed-save blocking, and idempotency no-duplication behavior.
- Marked P3 task `Generate embeddings only for confirmed create/update events` as completed in `TODO.md`.
- Added latency-aware transcription execution boundary for `POST /api/v1/voice/memory`: Whisper now supports `request_path` vs `background_worker` mode with configurable payload threshold (`VOICE_MEMORY_BACKGROUND_MIN_BYTES`) and optional override header (`x-ai-execution-mode`), while preserving the existing response contract.
- Added regression coverage for AI execution-mode resolution and Whisper background-worker dispatch behavior.
- Marked P3 task `Move expensive AI tasks (transcription/embeddings when applicable) to background jobs where latency requires it` as completed in `TODO.md`.
- Marked P3 task `Persist memory only after explicit confirmation` as completed in `TODO.md` after validating save-path guardrails (`confirmed=true` required) with confirmation-contract and ingestion E2E regression suites.
- Added explicit memory-confirmation contract regression coverage for ingestion flow: proposal actions (`Confirm/Modify/Cancel`), persistence rejection without confirmation (`memory.confirmation_required`), and successful persistence after confirmation.
- Marked P3 task `Confirmation contract: confirm/modify/cancel before persistence` as completed in `TODO.md`.
- Added configurable clarification turn limit for memory-ingestion follow-up questions (`MEMORY_CLARIFICATION_MAX_TURNS`, default `3`) and wired `POST /api/v1/voice/memory` to respect optional `x-clarification-turn` context.
- Updated clarification behavior to stop generating new clarification questions after max turns while preserving missing-field validation and confirmation gate.
- Extended regression coverage with dedicated clarification-engine tests and E2E route validation for turn-limit behavior.
- Marked P3 task `Clarification engine for missing fields (configurable max turns)` as completed in `TODO.md`.
- Normalized relative time expressions in memory ingestion (`today`, `yesterday`, `tomorrow`, `last week`, `next week`) to absolute UTC datetimes before confirmation proposal and before `/api/v1/memory` persistence when `structured_data.when` contains relative values.
- Extended ingestion regression coverage to verify relative-time normalization both in extraction proposal output and in save-memory persisted payload.
- Marked P3 task `Normalize relative time expressions (today/yesterday/tomorrow/etc.) to absolute date/time before confirmation and save` as completed in `TODO.md`.
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
- Marked Day 0 credentials/policy checklist item `Key naming convention defined` as completed in `TODO.md`.
- Marked Day 0 credentials/policy checklist item `Secret rotation cadence defined (recommended: every 90 days)` as completed in `TODO.md`.
- Marked Day 0 credentials/policy checklist item `Access revocation process defined for team offboarding` as completed in `TODO.md`.
- Marked Day 0 credentials/policy checklist item `Incident contact list documented (primary + backup)` as completed in `TODO.md`.
- Marked Day 0 credentials/policy checklist item `Billing alert thresholds defined (warning/critical)` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Confirm final stack` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Lock MVP language matrix and fallback policy` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Lock authentication policy for MVP` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Freeze MVP scope and non-goals in one source of truth document` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Define initial feature-flag governance model` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Resolve and lock canonical memory taxonomy and fields across all specs` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Assign owners for governance docs` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Define review cadence for governance docs` as completed in `TODO.md`.
- Marked P0 blocking checklist item `Define MVP KPIs` and all listed KPI thresholds as completed in `TODO.md`.
- Completed remaining P0 product-lock tasks in `TODO.md`: environment baseline definition, repository quality gates, pre-commit hooks, branding baseline, and baseline CI with lightweight security scan.
- Updated CI workflow (`.github/workflows/ci.yml`) to install backend/tooling dependencies and run the full quality-gate pipeline in automation.
- Updated local setup instructions in `README.md` to include pre-commit installation and full hook execution.
- Marked P1 task `Create modular FastAPI structure (api, services, repositories, domain)` as completed in `TODO.md`.
- Marked P1 task `Implement typed config management (env validation)` as completed in `TODO.md`.
- Marked P1 task `Set up JSON logging with request_id and user_id (when available)` as completed in `TODO.md`.
- Marked P1 task `Add request tracing (trace_id) to support cross-service debugging` as completed in `TODO.md`.
- Marked P1 task `Add error-handling middleware with standard error codes` as completed in `TODO.md`.
- Marked P1 task `Define asynchronous job boundary (API request path vs background worker path)` as completed in `TODO.md`.
- Marked P1 parent task `Health endpoints` as completed in `TODO.md` after validating existing health-route implementation coverage.
- Marked P1 task `GET /health/live` as completed in `TODO.md` after runtime `200` verification.
- Marked P1 task `GET /health/ready` as completed in `TODO.md` after runtime readiness verification (`200`, `status=ready`).
- Marked P1 task `Backend Dockerfile + local docker-compose with Postgres` as completed in `TODO.md` after compose baseline verification.
- Added `scripts/startup-smoke-check.ps1` for backend startup smoke validation (`docker compose config`, service health wait, `/health/live` and `/health/ready` checks) and documented it in `README.md`.
- Marked P1 task `Backend startup smoke test + health checks` as completed in `TODO.md`.
- Marked P2 task `Set up migrations (Alembic or equivalent)` as completed in `TODO.md` after successful migration smoke cycle (`upgrade -> verify -> downgrade -> verify -> restore`).
- Added Alembic revision `20260315_0002_enable_pgvector_extension.py` to enable `pgvector` (`vector` extension) and mark rollback support via downgrade.
- Marked P2 task `Enable pgvector extension` as completed in `TODO.md` after migration upgrade and DB extension verification.
- Added Alembic revision `20260315_0003_create_core_tables.py` to create core schema tables: `users`, `memories`, `memory_versions`, `attachments`, `embeddings`, and `qa_interactions`.
- Marked P2 task `Create tables: users, memories, memory_versions, attachments, embeddings, qa_interactions` as completed in `TODO.md` after migration and DB verification.
- Added Alembic revision `20260315_0004_add_user_billing_policy_constraints.py` to enforce `users` billing-policy constraints (`role` enum set, `subscription_plan` enum set, and role/billing-exempt/premium consistency policy).
- Marked P2 task `Add user billing-policy fields (role, subscription_plan, billing_exempt) with constraints` as completed in `TODO.md` after DB constraint verification.
- Added Alembic revision `20260315_0005_add_fks_constraints_indexes.py` to define foreign keys, memory-type constraint, and critical indexes on `user_id`/`created_at`/`memory_type`.
- Marked P2 task `Define FKs, constraints, and indexes on critical query fields (user_id, created_at, memory_type)` as completed in `TODO.md` after DB metadata verification and migration smoke checks.
- Added Alembic revision `20260315_0006_memory_versions_append_only.py` to enforce append-only version history (`memory_versions`) with positive `version_number`, unique `(memory_id, version_number)`, and DB trigger blocking `UPDATE`/`DELETE`.
- Marked P2 task `Implement memory versioning strategy (memory_versions append-only)` as completed in `TODO.md` after DB enforcement verification.
- Added repository-scoped memory access module `backend/app/repositories/memory_repository.py` with mandatory `tenant_id` + `user_id` scope validation for read/write queries.
- Updated memory/query routes to use repository access instead of direct fixture mutation (`memories`, `memory_ingestion`, `question`) to enforce user isolation consistently.
- Added `backend/tests/test_memory_repository_isolation.py` to verify repository-level scope requirements and tenant/user filtering behavior.
- Marked P2 task `Enforce per-user isolation policy across all repository queries` as completed in `TODO.md`.
- Added tenant-ready schema baseline doc `TENANT_READY_SCHEMA_STRATEGY.md` and Alembic revision `20260315_0007_prepare_tenant_ready_schema.py` to add non-null `tenant_id` + tenant indexes/checks on core user-scoped tables.
- Marked P2 task `Prepare tenant-ready schema strategy (tenant_id support) for B2B isolation path` as completed in `TODO.md` after schema/index verification.
- Added `backend/app/core/idempotency.py` with tenant/user/path-scoped idempotency store and payload hashing for safe write retries.
- Updated `POST /api/v1/memory` in `backend/app/api/routes/memory_ingestion.py` to honor `Idempotency-Key`: replay same response on retry and reject key reuse with different payload.
- Added `backend/tests/test_memory_idempotency.py` to verify duplicate-prevention behavior and mismatch rejection.
- Added Alembic revision `20260315_0008_soft_delete_and_audit_strategy.py` introducing soft-delete fields on `memories` (`deleted_at`, `deleted_by_user_id`, `delete_reason` + index) and `memory_audit_log` with constrained actions (`update/delete/restore`), relational links, and query indexes for sensitive-operation auditing.
- Added `SOFT_DELETE_AUDIT_STRATEGY.md` documenting the operational strategy for soft-delete and audit trail handling on sensitive memory updates/deletes.
- Added Alembic revision `20260315_0009_add_structured_data_schema_version.py` to introduce `structured_data_schema_version` on `memories` and `memory_versions` with default `1` and positive-version check constraints for forward-compatible payload evolution.
- Added deterministic local seed dataset SQL `scripts/sql/local-test-seed.sql` covering realistic tenant-scoped users, memories (including soft-delete case), memory versions, attachments, QA interactions, and memory-audit entries for development and integration checks.
- Added `scripts/seed-local-test-dataset.ps1` to apply/verify the local seed dataset against Docker Postgres with strict failure handling and row-count summary output.
- Added `backend/app/services/audio_upload.py` with robust voice-upload validation for `/api/v1/voice/memory` (allowed audio MIME types, 5 MB max payload size, and explicit empty-payload rejection).
- Added `backend/tests/test_voice_memory_upload_validation.py` covering unsupported content type, empty audio payload, and over-limit upload rejection for voice-memory ingestion.
- Added `backend/app/services/whisper_transcription.py` with Whisper transcription integration, controlled timeout/retry behavior, and deterministic local fallback when OpenAI key is not configured.
- Added `backend/tests/test_whisper_transcription.py` covering Whisper fallback, timeout retry-success path, retry exhaustion (`503 ai.provider_unavailable`), and non-retryable provider error mapping.
- Added API versioning folder structure `backend/app/api/v1/routes` and migrated route modules into the versioned package.
- Added compatibility layer modules under `backend/app/api/routes/*` forwarding to `app.api.v1.routes.*` to preserve legacy import paths during transition.
- Added versioned extraction prompt module `backend/app/services/prompts/memory_extraction_prompt.py` with stable prompt identifier `memory_extraction_v1` and reusable prompt builder.
- Added `backend/tests/test_memory_extraction_prompt_versioning.py` to enforce prompt version format and canonical memory-type coverage in the extraction prompt contract.
- Added clarification model/prompt registry baseline in `docs/model-registry.md` (`clarification_generation`, `gpt-4o-mini`, `mvp-v1`, `clarification_v1`) with explicit fallback entry and validation timestamp.
- Added `backend/tests/test_memory_type_classification.py` to lock canonical memory-type classification behavior across all MVP types (`expense_event`, `inventory_event`, `loan_event`, `note`, `document`).
- Added `backend/tests/test_required_fields_by_type_contract.py` to enforce required-by-type persistence contract coverage, including alias fields (`item/what`, `person/counterparty`, `what/content`) and document attachment requirement.
- Added `backend/tests/test_semantic_field_extraction.py` to validate typed semantic extraction for `who/what/where/when/why/how` across memory ingestion proposals.
- Marked P2 task `Add idempotency strategy for write endpoints to prevent duplicate memory creation on retries` as completed in `TODO.md`.
- Marked P2 task `Add soft-delete + audit trail strategy for sensitive memory operations (update/delete)` as completed in `TODO.md`.
- Updated memory API contracts and runtime payload handling to include `structured_data_schema_version` (default `1`) in save/list flows and OpenAPI schema definitions (`SaveMemoryRequest`, `MemoryRecord`).
- Marked P2 task `Add structured_data_schema_version support for forward-compatible payload evolution` as completed in `TODO.md`.
- Updated `README.md` local startup sequence to include deterministic local test dataset seeding.
- Updated CI workflow (`.github/workflows/ci.yml`) to execute `scripts/migration-smoke-check.ps1` after quality gates, enforcing migration upgrade/downgrade/restore verification in automation.
- Updated `/api/v1/voice/memory` upload handling to enforce robust audio validation before extraction and aligned OpenAPI/spec coverage for 422 upload-validation failures.
- Updated `/api/v1/voice/memory` transcription path to use Whisper service integration with controlled retries and `503` response contract for provider unavailability.
- Updated `.env.example` with Whisper runtime controls (`WHISPER_TIMEOUT_SECONDS`, `WHISPER_MAX_RETRIES`).
- Updated backend router wiring in `backend/app/main.py` to import from `app.api.v1.routes.*`.
- Updated memory-ingestion telemetry wiring to use centralized extraction prompt version constant instead of route-local hardcoded value.
- Updated `docs/model-registry.md` active mapping date to `2026-03-15` and aligned rollback entries to include clarification generation fallback.
- Validated memory-type classifier contract against canonical taxonomy with dedicated regression tests and marked the P3 classification task as completed.
- Updated `backend/app/services/memory_ingestion.py` required-field enforcement to align with canonical `required_by_type` contract: expense (`item|what`, `amount`, `currency`), inventory (`item`, `quantity`, `action`), loan (`person|counterparty`, `amount`, `currency`, `action`), note (`what|content`), document (`what|content` + attachment link).
- Updated extraction heuristics to infer `currency` and loan `action` (`lend`/`borrow`) where present in transcript, reducing unnecessary clarification loops.
- Updated memory-ingestion extraction heuristics to populate semantic fields (`who`, `what`, `where`, `when`, `why`, `how`) from transcript context while preserving deterministic, typed field extraction.
- Updated memory-ingestion proposal flow to apply default `when` as current UTC timestamp when transcript does not include explicit date/time, while preserving explicit extracted `when` values.
- Extended semantic extraction regression coverage to validate default-`when` behavior and explicit-date preservation.
- Updated impacted tests to satisfy strengthened expense required-field contract (`currency` required) in end-to-end, attachment, and AI-cost metric flows.
- Marked P2 task `Create realistic local seed dataset for tests` as completed in `TODO.md`.
- Marked P2 task `Test migration up/down in CI` as completed in `TODO.md`.
- Marked P3 task `Endpoint POST /api/v1/voice/memory with robust audio upload handling` as completed in `TODO.md`.
- Marked P3 task `Whisper integration with timeout and controlled retry` as completed in `TODO.md`.
- Marked dedicated API folder versioning refactor task as completed in `TODO.md`.
- Marked P3 task `Versioned extraction prompt (specs/memory-extraction.md)` as completed in `TODO.md`.
- Marked P3 task `Register extraction/clarification model + prompt versions in docs/model-registry.md` as completed in `TODO.md`.
- Marked P3 task `memory_type classification (expense_event, inventory_event, loan_event, note, document)` as completed in `TODO.md`.
- Marked P3 task `Enforce required fields per memory_type before persistence (required_by_type contract)` as completed in `TODO.md`.
- Marked P3 task `Typed + semantic field extraction (who/what/where/when/why/how)` as completed in `TODO.md`.
- Marked P3 task `Apply default when = current timestamp when user does not provide explicit date/time` as completed in `TODO.md`.
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



















