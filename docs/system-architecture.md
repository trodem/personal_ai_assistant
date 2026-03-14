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
6. Notification Layer (transactional email)

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
Admin user management (admin/author role)
Author supervision dashboard (author role only)

Voice interaction uses **push-to-talk recording**.

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

Responsibilities:

user registration
login
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
