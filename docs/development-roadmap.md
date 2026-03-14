# Development Roadmap

This document defines the development sequence for the Personal AI Assistant.

The goal is to build a functional MVP with the correct architecture.

The roadmap prioritizes backend and data infrastructure before user interface development.

---

# Phase 1 - Backend Foundation

Goal: Create the core backend service.

Tasks:

* Initialize FastAPI project
* Setup project structure
* Configure environment variables
* Setup logging
* Configure basic health endpoints

Deliverable:

Running backend server.

---

# Phase 2 - Database Setup

Goal: Create the database schema.

Tasks:

* Setup Supabase Postgres
* Enable pgvector extension
* Create database tables

Tables:

users
memories
memory_versions
attachments
embeddings

Deliverable:

Working database with migrations.

---

# Phase 3 - AI Pipeline Core

Goal: Implement the AI pipeline.

Tasks:

* Integrate Whisper transcription
* Implement memory extraction
* Implement clarification logic
* Implement confirmation system
* Define model/prompt mappings in `docs/model-registry.md` for extraction, clarification, question NLG, and embeddings

Deliverable:

Voice memory processing working end-to-end.

---

# Phase 4 - API Endpoints

Goal: Build backend APIs.

Endpoints:

POST /api/v1/voice/memory
POST /api/v1/voice/question
POST /api/v1/question
POST /api/v1/memory
GET /api/v1/memories
DELETE /api/v1/memory/{id}
POST /api/v1/attachments
GET /api/v1/dashboard
GET /api/v1/me/settings
PATCH /api/v1/me/settings/profile
PATCH /api/v1/me/settings/security
PATCH /api/v1/me/settings/notifications
GET /api/v1/notifications
POST /api/v1/notifications/{id}/read
GET /api/v1/admin/users
PATCH /api/v1/admin/users/{id}/status
PATCH /api/v1/author/users/{id}/role
GET /api/v1/author/dashboard

Deliverable:

Complete backend API.

---

# Phase 5 - Authentication

Goal: Secure user access.

Tasks:

* Integrate Supabase Auth
* Enable Supabase OAuth SSO providers (Google, Apple)
* Validate tokens in backend
* Connect users to database records
* Implement 2FA/TOTP enrollment and verification flow
* Enforce role-based 2FA policy (`admin`/`author` mandatory, `user` optional)

Deliverable:

Authenticated users.

---

# Phase 6 - Semantic Search and Question Engine

Goal: Enable semantic retrieval and AI question answering.

Tasks:

* Implement embedding generation
* Store embeddings
* Implement vector search
* Implement intent detection
* Implement database-first query execution
* Generate final natural-language response

Deliverable:

Users can ask questions about stored memories with accurate, database-grounded answers.

---

# Phase 7 - Mobile Application

Goal: Build Flutter app.

Tasks:

* Create Flutter project
* Implement voice recording
* Implement memory confirmation UI
* Implement assistant response UI
* Implement i18n localization framework (`en`, `it`, `de`) with English fallback
* Add settings language selector and backend sync (`preferred_language`)
* Implement guided onboarding wizard (welcome -> language -> permissions -> first memory -> first question)
* Persist onboarding completion and support skip/resume behavior
* Implement AI interaction UX rules from `docs/ai-ux-contract.md` (clarification, confirmation, answer explainability, error states)

Deliverable:

Working mobile interface.

---

# Phase 8 - Dashboard

Goal: Provide user insights.

Features:

recent memories
expense summaries
inventory summaries
loan tracking

Deliverable:

Dashboard screen.

---

# Phase 9 - Attachments

Goal: Allow receipt photo uploads only.

Tasks:

* Implement Supabase Storage integration
* Upload receipt photos (`jpg`, `jpeg`, `png`, `webp`, `heic`)
* Reject PDF and any non-image upload
* Run OCR on uploaded receipt photos
* Feed OCR text into memory extraction proposal flow
* Enforce no auto-save after scan (save only after `Confirm`)
* Link attachments to memories

Deliverable:

Memories with attachments.

---

# Phase 10 - Billing

Goal: Enable subscriptions.

Tasks:

* Integrate Stripe
* Create subscription plans
* Validate subscription status
* Add in-app settings plan management (upgrade/downgrade)
* Trigger transactional notifications for billing/account security events

Deliverable:

Freemium model working.

---

# Phase 10.5 - Admin and Settings

Goal: Add account administration and self-service settings.

Tasks:

* Add role model (`user`, `admin`, `author`) and account status (`active`, `suspended`, `canceled`)
* Build admin user management APIs and UI (list/search/suspend/reactivate/cancel)
* Build author role-management APIs/UI (`user` <-> `admin`) and global supervision dashboard
* Build user settings APIs and UI (profile, security, subscription)
* Build notifications UX (in-app notification center + channel preferences for in-app/push/email)
* Enforce RBAC and audit logs for admin/author actions
* Enforce author safety invariants (no self-role-change, no self-suspend/cancel, keep at least one active author)
* Enforce role-based billing lock (`admin`/`author` always premium + billing-exempt)

Deliverable:

Operational admin management + user self-service settings.

---

# Phase 11 - Production Preparation

Goal: Prepare for deployment.

Tasks:

* Dockerize backend
* Deploy backend to cloud runtime with at least 2 instances in staging/prod
* Configure managed load balancer with health-check routing (`/health/live`, `/health/ready`)
* Configure autoscaling thresholds (CPU/memory/latency) and scale limits
* Configure zero-downtime rollout strategy (rolling or blue/green)
* Configure environment secrets
* Setup monitoring
* Implement product analytics event tracking based on `docs/product-analytics.md`
* Validate KPI dashboards from canonical event stream
* Setup deployment pipeline

Deliverable:

Production-ready system.
