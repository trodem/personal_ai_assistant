# Product Analytics Contract

## Purpose

Define a single event taxonomy for product behavior analytics and operational quality signals.

This contract prevents ad-hoc event names and inconsistent metric definitions.

---

## Scope

This document covers:

- product usage events (user behavior)
- reliability/error events (operational behavior)
- event naming and payload conventions
- privacy and retention constraints

---

## Naming Rules

- event names use `snake_case`
- event names are immutable once released
- event payload keys use `snake_case`
- timestamps are UTC ISO-8601
- amounts must include explicit currency

---

## Required Common Fields

Every analytics event must include:

- `event_name`
- `event_version`
- `event_id` (uuid)
- `occurred_at` (UTC)
- `user_id` (nullable only for pre-auth events)
- `session_id`
- `platform` (`ios`, `android`, `backend`)
- `app_version`

Optional but recommended:

- `request_id`
- `trace_id`

---

## Product Event Taxonomy (MVP)

Onboarding and auth:

- `auth_signup_completed`
- `auth_login_completed`
- `auth_sso_login_completed`
- `auth_mfa_enabled`
- `auth_mfa_challenge_passed`
- `onboarding_started`
- `onboarding_step_viewed`
- `onboarding_permissions_granted`
- `onboarding_skipped`
- `onboarding_completed`

Memory flow:

- `memory_input_started`
- `memory_extraction_proposed`
- `memory_clarification_requested`
- `memory_clarification_answered`
- `memory_confirmed`
- `memory_modified`
- `memory_canceled`
- `memory_persisted`

Question flow:

- `question_asked`
- `question_answered`
- `question_no_result`
- `question_ambiguous`
- `answer_feedback_submitted`

Attachment flow:

- `attachment_upload_started`
- `attachment_upload_completed`
- `attachment_ocr_started`
- `attachment_ocr_completed`
- `attachment_proposal_ready`
- `attachment_persisted`
- `attachment_failed`

Billing and settings:

- `plan_upgrade_requested`
- `plan_downgrade_requested`
- `plan_changed`
- `subscription_cancel_previewed`
- `subscription_cancel_reason_submitted`
- `subscription_retained`
- `subscription_canceled`
- `settings_profile_updated`
- `settings_security_updated`
- `settings_notification_preferences_updated`

Notifications:

- `notification_sent`
- `notification_delivered`
- `notification_failed`
- `notification_opened`
- `notification_marked_read`

Safety and privacy:

- `moderation_blocked`
- `moderation_warned`
- `moderation_review_flagged`
- `prompt_sanitized`
- `privacy_redaction_applied`

Experiments and rollout:

- `feature_flag_exposed`
- `experiment_exposed`
- `experiment_converted`

---

## Operational/Error Events (MVP)

- `api_error_4xx`
- `api_error_5xx`
- `dependency_error_openai`
- `dependency_error_supabase`
- `dependency_error_stripe`
- `rate_limit_triggered`
- `job_retry_scheduled`
- `job_dead_lettered`

Error code values must align with `docs/error-model.md`.

---

## Funnel Definitions (MVP)

First memory funnel:

1. `memory_input_started`
2. `memory_extraction_proposed`
3. `memory_confirmed`
4. `memory_persisted`

First question funnel:

1. `question_asked`
2. `question_answered`

Onboarding activation funnel:

1. `onboarding_started`
2. `onboarding_step_viewed` (language + permissions)
3. `memory_persisted` (first memory)
4. `question_answered` (first question)
5. `onboarding_completed`

Receipt funnel:

1. `attachment_upload_completed`
2. `attachment_ocr_completed`
3. `attachment_proposal_ready`
4. `memory_confirmed`
5. `memory_persisted`

---

## KPI Mapping

- `memory_save_success_rate` = `memory_persisted / memory_input_started`
- `extraction_confirmation_rate` = `memory_confirmed / memory_extraction_proposed`
- `time_to_first_successful_memory` = first `memory_persisted` - first `auth_login_completed`
- `question_success_rate` = `question_answered / question_asked`
- `onboarding_completion_rate` = `onboarding_completed / onboarding_started`
- `answer_feedback_positive_rate` = `like / (like + dislike)`
- `subscription_retention_rate_after_cancel_preview` = `subscription_retained / subscription_cancel_previewed`
- `experiment_variant_conversion_rate` = `experiment_converted / experiment_exposed` (per experiment variant)

---

## Privacy and Compliance Rules

- never store raw secrets/tokens in analytics events
- avoid raw PII in event payloads; use IDs and coarse categories
- redact sensitive free-text unless explicitly required and approved
- retention policy must follow project GDPR baseline in `TODO.md` and security docs

---

## Validation and Governance

- schema validation required for tracked events in tests
- event additions/changes must update this document and `CHANGELOG.md`
- breaking event changes require explicit version bump (`event_version`)
