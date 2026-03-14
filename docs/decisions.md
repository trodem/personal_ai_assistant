# Architecture Decisions

This document records all major technical and product decisions made during the design of the Personal AI Assistant.

The purpose is to prevent architectural drift and ensure consistent development.

---

# Product Positioning

Product type: **Memory Assistant**

The assistant focuses on storing and retrieving real-world personal information rather than acting as a general conversational AI.

Examples of use cases:

* tracking expenses
* remembering locations of objects
* tracking loans
* storing notes and receipt photos linked to memories

---

# Input Method

Primary input method: **voice**

Interaction model:

Push-to-talk recording.

Users press a button, record audio, and upload it to the backend.

Always-on listening is not supported in the MVP.

---

# Voice Processing

Voice processing occurs in the backend.

Pipeline:

User audio
->
Backend upload
->
Whisper speech-to-text

Speech recognition is not performed locally on the device.

---

# AI Pipeline Architecture

The system uses a **multi-stage AI pipeline**.

Pipeline:

Speech-to-text (Whisper)
->
Memory extraction (LLM)
->
Clarification if needed
->
User confirmation
->
Database storage

AI is also used for generating natural language responses to questions.

---

# Database Strategy

Database: PostgreSQL

Vector search: pgvector extension.

Provider: Supabase Postgres.

The database stores:

users
memories
memory_versions
attachments
embeddings

---

# Memory Model

The system uses an **event-based memory model**.

Examples:

Inventory events
Loan events
Expense events

Events are stored individually and the system computes the current state dynamically.

---

# Memory Structure

Memories use **typed fields**, not only JSON.

Examples of fields:

item
location
person
quantity
amount
currency
action

This allows efficient database queries and analytics.

---

# Memory Versioning

Memory records support versioning.

Each modification creates a new version.

Previous versions remain stored for history and audit purposes.

---

# User Isolation

All data is isolated per user.

Each table includes a user_id field.

Users cannot access other users' data.

---

# Platform Provider Decision

Supabase is the default platform for core backend services:

- Supabase Auth for authentication
- Supabase Postgres for primary relational storage
- Supabase Storage for receipt-photo attachments

Alternative auth/storage providers are out of scope for MVP unless explicitly re-approved.

---

# Authentication Policy

Authentication provider: Supabase Auth.

MVP auth modes:

- email/password
- SSO via OAuth providers (`Google`, `Apple`)

2FA policy:

- 2FA must be available to all users
- 2FA is mandatory for `admin` and `author` roles
- privileged operations should be blocked if mandatory 2FA is not enabled

---

# Roles and Administration

The system supports role-based access:

user
admin
author

Admin capabilities include user management actions (for example suspend/reactivate/cancel), protected by RBAC and audit logging.
Author is the highest role and can also manage user roles (`user` <-> `admin`) plus access global supervision dashboards.

Author safety constraints:

- author cannot change own role
- author cannot suspend/cancel own account
- system must keep at least one active author

---

# Attachments

Memories can include attachments.

Examples:

photos
receipts
receipt photos only (no PDF/documents in MVP)

Files are stored in cloud object storage.

The database stores only file metadata and URLs.

---

# Query Execution Strategy

Database-first execution.

The backend performs calculations such as:

sum
filter
aggregation

The AI model generates only the final natural language response.

---

# Voice API Design

Separate endpoints are used for voice processing.

POST /api/v1/voice/memory
POST /api/v1/voice/question
POST /api/v1/question

This avoids ambiguity and simplifies backend logic.

---

# API Versioning Policy

All HTTP endpoints must be exposed under a versioned prefix.

Current version:

/api/v1

Rules:

- new endpoints must be published under `/api/v1/...`
- docs, OpenAPI spec, and implementation must stay aligned on the same versioned paths
- unversioned aliases are out of scope for MVP

---

# Pricing Model

Freemium SaaS model.

Free plan:

limited memories
limited questions

Premium plan:

10-15 EUR per month

Premium features:

unlimited memories
receipt photo attachments
advanced insights

Role-based billing rule:

- `admin` and `author` are always `premium` and billing-exempt

---

# Notification Policy

Notification system supports three channels:

in-app
push
email

MVP requirements:

- transactional security/billing events must trigger notifications
- users can manage channel preferences in settings
- in-app notifications must support read/unread state

---

# Long-Term Model Flexibility

The AI architecture is designed to support multiple models.

Initial model provider:

OpenAI

Future support may include:

Anthropic
local models
other providers

Model/prompt version governance is managed in `docs/model-registry.md` and must be updated on every model routing or prompt change.
