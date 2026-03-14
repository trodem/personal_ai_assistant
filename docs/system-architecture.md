# System Architecture

This document describes the technical architecture of the Personal AI Assistant.

The system is designed to be:

* scalable
* modular
* cloud-native
* AI-ready

---

# High-Level Architecture

The platform consists of five main components:

1. Mobile Application (Flutter)
2. API Backend
3. AI Processing Layer
4. Database Layer
5. Storage Layer
6. Notification Layer (in-app + push + email)

System overview:

Mobile App
->
API Backend
->
AI Pipeline
->
Database + Vector Search
->
Supabase Storage

---

# Mobile Application

Technology:

Flutter + Dart

Responsibilities:

* voice recording
* user interface
* memory confirmation
* displaying answers
* dashboard visualization
* authentication

Main screens:

Home
Memory recording
Question recording
Dashboard
Memory list
Settings
Onboarding wizard (first-run only)
Admin user management (admin/author role)
Author supervision dashboard (author role only)

Voice interaction uses **push-to-talk recording**.

Localization policy (MVP):

- supported languages: English (`en`), Italian (`it`), German (`de`)
- UI fallback language: English (`en`)
- user-selected locale is managed in settings and propagated to backend preference (`preferred_language`)

Onboarding policy (MVP):

- guided first-run flow is required for new users
- sequence: welcome -> language -> permissions -> first memory -> first question
- onboarding must be resumable and stored as completion state

---

# API Backend

Technology:

Python (FastAPI)

Responsibilities:

* API endpoints
* authentication validation
* AI orchestration
* database queries
* memory processing
* attachment uploads
* role-based user administration
* account settings management
* billing plan changes
* transactional notification triggers
* in-app notification feed and read-state updates

User account status model:

active
suspended
canceled

Role model:

user
admin
author

Example endpoints:

POST /api/v1/voice/memory
POST /api/v1/voice/question
POST /api/v1/question
POST /api/v1/memory
GET /api/v1/memories
DELETE /api/v1/memory/{id}
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

The backend controls all AI interactions.

---

# AI Processing Layer

The AI system follows a multi-stage pipeline.

Voice pipeline:

Audio
->
Whisper transcription
->
Memory extraction
->
Clarification
->
Confirmation
->
Database storage

Receipt-photo pipeline:

Receipt photo (camera/gallery)
->
Upload validation
->
Object storage
->
OCR extraction
->
Memory extraction proposal
->
Clarification + confirmation
->
Database storage

Question pipeline:

Audio or text question
->
Whisper transcription (voice only)
->
Intent detection
->
Database query
->
LLM response generation

AI is used only for language understanding and natural responses.

Calculations are always handled by the backend.

Query/answer language policy:

- answer language should follow `preferred_language` when available
- if preferred language output is unavailable, fallback to English with no silent mixed-language fragments

---

# Database Layer

Technology:

PostgreSQL

Provider:

Supabase Postgres

Extension:

pgvector

Tables include:

users
memories
memory_versions
attachments
embeddings

PostgreSQL handles:

structured queries
aggregations
user isolation
vector search

---

# Vector Search

Vector search enables semantic retrieval of memories.

Example:

User question:

"Where did I put the drill?"

The system generates an embedding and retrieves similar memories.

Embeddings are stored using pgvector.

---

# Object Storage

Files are stored in cloud object storage.

Examples:

Supabase Storage

Stored files include:

photos
receipts
receipt-photo attachments only (no PDF/documents in MVP)

The database stores only file URLs.

---

# Authentication

Authentication is handled by an external identity provider.

Provider:

Supabase Auth

SSO policy (MVP):

Google OAuth
Apple OAuth

2FA policy:

- `admin` and `author` must have 2FA enabled
- `user` can enable 2FA optionally

Responsibilities:

user registration
login
SSO login
2FA challenge/verification
session validation
subscription status

The backend trusts the authentication provider.

---

# Subscription and Billing

Subscriptions are required for premium features.

Recommended provider:

Stripe

Responsibilities:

subscription management
payment processing
billing events
plan upgrades

The backend checks subscription status before allowing premium features.

Users can manage plan changes in settings (`free` <-> `premium`) through backend billing orchestration.

Role-based billing policy:

- `admin` and `author` are always `premium`
- `admin` and `author` are billing-exempt

---

# Transactional Notifications

Critical account and billing events must trigger automatic notifications.

Examples:

email change
password change
account suspension/reactivation
plan change and billing failures

Provider is abstracted behind backend service (provider choice decided separately).

Notification channels:

in-app
push
email

Users must be able to configure channel preferences in settings.

Author safety invariants:

- self-role change is forbidden
- self-suspend/self-cancel is forbidden
- last active author cannot be removed

---

# Scalability Strategy

The architecture supports scaling through:

stateless backend services
cloud object storage
PostgreSQL scaling
vector indexing

AI workloads are handled by external AI APIs.

Infrastructure scaling baseline (required for staging/prod):

- cloud deployment with at least two backend instances per environment
- managed load balancer in front of backend instances
- health-check based routing using `/health/live` and `/health/ready`
- horizontal autoscaling policy based on CPU, memory, and request latency
- zero-downtime rollout strategy (rolling or blue/green)
- rate limiting and timeout policy enforced at edge/load-balancer layer

---

# Security Principles

Key security rules:

users can access only their own data
all API requests require authentication
files are stored securely in cloud storage
AI cannot modify data without confirmation

Sensitive operations require backend validation.

---

# Future Infrastructure Improvements

Future versions may include:

background job workers
caching layer
AI model routing
analytics pipeline
multi-region deployment

---

# Product Analytics

Product and operational analytics must follow `docs/product-analytics.md`.

Event tracking must cover:

- onboarding and activation funnels
- memory/question/attachment flow outcomes
- notification engagement
- operational error classes and dependency failures

---

# AI UX Governance

AI interaction behavior must follow `docs/ai-ux-contract.md`.

This includes clarification cadence, confirm/modify/cancel flow, explainability UX, and user-visible state transitions.

---

# Model and Prompt Governance

Model and prompt versions must be managed through `docs/model-registry.md`.

All AI use-cases (transcription, extraction, clarification, question phrasing, embeddings) must map to explicit active model entries with rollback targets.
