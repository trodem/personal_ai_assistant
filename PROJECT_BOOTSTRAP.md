# PROJECT BOOTSTRAP

This file instructs the AI agent how to start working on the Personal AI Assistant project.

The agent must follow these rules strictly.

---

# STEP 1 - READ PROJECT CONTEXT

Before performing any action the agent must read:

PROJECT_CONTEXT.md

This file contains the entire system specification.

No architectural decision may be ignored.

---

# STEP 2 - CONFIRM UNDERSTANDING

After reading the context, the agent must summarize:

System architecture
AI pipeline
Database schema
Memory model
Product positioning

Only after confirming understanding may implementation begin.

---

# STEP 3 - IMPLEMENTATION PRIORITY

The implementation must follow this order:

1. Backend foundation
2. Database schema
3. AI pipeline
4. API endpoints
5. Authentication
6. Mobile application
7. Dashboard
8. Attachments
9. Billing integration

The agent must never start with UI before backend APIs exist.

---

# STEP 4 - BACKEND FOUNDATION

The backend must be built first.

Technology:

Python
FastAPI

Required modules:

auth
memory
events
query
attachments
ai_pipeline

---

# STEP 5 - DATABASE SETUP

Database:

PostgreSQL

Provider:

Supabase Postgres

Required extension:

pgvector

Tables:

users
memories
memory_versions
attachments
embeddings

---

# STEP 6 - AI PIPELINE IMPLEMENTATION

The AI pipeline must implement:

Speech-to-text using Whisper
Memory extraction using LLM
Clarification system
Confirmation system
Question answering pipeline

AI must never perform calculations.

All calculations must be performed in the backend.

---

# STEP 7 - API IMPLEMENTATION

Required endpoints:

POST /api/v1/voice/memory
POST /api/v1/voice/question
POST /api/v1/question
POST /api/v1/memory
GET /api/v1/memories
DELETE /api/v1/memory/{id}
POST /api/v1/attachments
GET /api/v1/dashboard
GET /api/v1/admin/users
PATCH /api/v1/admin/users/{id}/status
GET /api/v1/author/dashboard
PATCH /api/v1/author/users/{id}/role
GET /api/v1/me/settings
PATCH /api/v1/me/settings/profile
PATCH /api/v1/me/settings/security
POST /api/v1/billing/subscription/change-plan

The API must enforce user authentication.
Role and permission enforcement must follow `docs/rbac-matrix.md`.

---

# HARD START BLOCKERS

Do not start implementation until these are true:

Supabase project is reachable (Auth + Postgres + Storage)
OpenAI API key is valid and billing-enabled
.env.example is complete for local boot
Owner and backup owner are assigned in the operational registry
MFA is enabled on critical provider accounts

If any blocker is unresolved, stop and report it before coding.

---

# STEP 8 - MOBILE APPLICATION

Technology:

Flutter + Dart

Main screens:

Home
Add Memory
Ask Assistant
Dashboard
Memory History

Voice recording must use push-to-talk.

---

# STEP 9 - STORAGE

Attachments must be stored in cloud object storage.

MVP attachment policy:

- only receipt photos are allowed (jpg, jpeg, png, webp, heic)
- PDF and non-image files must be rejected
- upload/scan alone must never persist memory
- OCR output must go through normal clarification + confirmation flow

Provider:

Supabase Storage

The database stores only file metadata.

---

# STEP 10 - AUTHENTICATION

Authentication must use an external provider.

Recommended provider:

Supabase Auth

The backend validates authentication tokens.
MVP auth methods include email/password and OAuth SSO (`Google`, `Apple`).
2FA must be available for all users and mandatory for `admin`/`author`.
Account status (`active`, `suspended`, `canceled`) must be enforced on protected endpoints.
RBAC (`user`, `admin`, `author`) must be enforced on privileged endpoints.

---

# STEP 11 - BILLING

Billing must use Stripe.

Required features:

subscription plans
payment processing
subscription validation

Premium features must require active subscription.
Role policy exception:
- `admin` and `author` are always `premium`
- `admin` and `author` are billing-exempt
- role policy must follow `docs/rbac-matrix.md` and `docs/monetization.md`

---

# STEP 12 - DEVELOPMENT PRINCIPLES

The system must follow these principles:

modular architecture
event-based memory model
database-first calculations
AI only for language reasoning
strict user data isolation

---

# STEP 13 - SAFETY RULES

The agent must never:

modify architecture decisions
change memory model
remove confirmation system
allow cross-user data access

All sensitive actions require confirmation.

---

# STEP 14 - FUTURE EXTENSIONS

The architecture must allow future support for:

multiple AI providers
local AI models
business accounts
advanced analytics

