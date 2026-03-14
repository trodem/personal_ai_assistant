# PROJECT CONTEXT

This document contains the complete specification of the Personal AI Assistant project.

The purpose of this file is to allow the project to continue in new conversations without losing architectural decisions or system design.

The assistant must read this document fully before answering.

---

# PROJECT OVERVIEW

The project is a **Personal AI Memory Assistant**.

The assistant helps users:

* remember real world information
* track objects
* track expenses
* track loans
* store receipt photos linked to memories
* ask questions about past events

The product acts as a **second brain** for real-life information.

The assistant focuses on **memory and life tracking**, not general AI chat.

---

# CORE PRODUCT IDEA

Users interact with the assistant primarily through **voice input**.

The application has two primary actions:

Add Memory
Ask Assistant

Example memory input:

"I put four boxes of peas in the cellar."

Example question:

"How many peas are left in the cellar?"

---

# INPUT MODEL

Primary input method:

Voice

Interaction model:

Push-to-talk recording

Process:

User taps button
Records voice
Audio uploaded to backend
Processed by AI pipeline

Always-on listening is not supported in MVP.

---

# VOICE PROCESSING

Voice processing is performed in the backend.

Pipeline:

User Audio
->
Backend Upload
->
Whisper Speech-to-Text
->
Text Processing

Speech recognition is not done on the device.

---

# AI PIPELINE

The system uses a **multi-stage AI pipeline**.

Memory pipeline:

Audio
->
Whisper transcription
->
LLM memory extraction
->
Clarification questions if needed
->
User confirmation
->
Memory stored in database

Question pipeline:

Audio
->
Whisper transcription
->
Intent detection
->
Database query
->
LLM generates natural response

AI does not perform calculations.

All calculations are handled by the backend and database.

---

# MEMORY MODEL

The system uses an **event-based memory model**.

Memories are stored as events.

Examples:

Inventory changes
Loan transactions
Expense events

Example:

User says:

"I put four boxes of peas in the cellar."

Stored event:

inventory_event
item: peas
location: cellar
quantity: 4
action: add

Later:

"I took two boxes."

Stored event:

inventory_event
item: peas
location: cellar
quantity: 2
action: remove

The system calculates the current state dynamically.

---

# MEMORY TYPES

Supported memory types:

expense_event
inventory_event
loan_event
note
document

---

# SEMANTIC CONTEXT

Each memory may contain semantic fields:

who
what
where
when
why
how

These fields allow better reasoning and search.

---

# CLARIFICATION SYSTEM

If the information provided by the user is incomplete, the assistant asks follow-up questions.

Example:

User:

"I bought bread."

Assistant asks:

Where did you buy it?
How much did you pay?

After clarification, the assistant proposes a structured memory.

The user must confirm before saving.

---

# CONFIRMATION RULE

Memories are never saved automatically.

The assistant always shows the extracted structure.

Example:

Type: expense_event
Item: bread
Location: Coop
Amount: 3 CHF

User must choose:

Confirm
Modify
Cancel

Only confirmed memories are stored.

---

# DATABASE

Database technology:

PostgreSQL

Provider:

Supabase Postgres

Extension:

pgvector

Tables:

users
memories
memory_versions
attachments
embeddings

---

# USER ISOLATION

All records include:

user_id

Users cannot access data belonging to other users.

---

# MEMORY VERSIONING

Memories support versioning.

Each modification creates a new version.

Previous versions remain stored for audit and history.

---

# ATTACHMENTS

Memories may include attachments.

Examples:

photos
receipts
receipt photos only (no PDF/documents/contracts in MVP)

User attachment UX must support both:

Take Photo
Choose from Gallery

After upload, the backend must run OCR and feed the extracted text into the normal memory extraction flow.

Attachment scan/upload alone must not save memory automatically; `Confirm` is still required.

Attachment lifecycle must be deterministic:

uploaded
ocr_processing
proposal_ready
confirmed or failed

Orphan uploads (never confirmed) must be cleaned by retention policy.

Files are stored in cloud object storage.

The database stores only metadata and file URLs.

---

# VECTOR SEARCH

Vector search enables semantic retrieval.

Process:

User question
->
Embedding generation
->
Vector search
->
Relevant memories retrieved
->
LLM generates answer

Embeddings stored using pgvector.

---

# QUERY EXECUTION STRATEGY

Database-first approach.

The backend performs:

sum
filter
aggregation

AI only generates the final natural language response.

---

# API DESIGN

Voice endpoints are separated.

Endpoints:

POST /voice/memory
POST /voice/question

Other endpoints:

POST /memory
GET /memories
DELETE /memory/{id}
POST /attachments
GET /dashboard
GET /me/settings
PATCH /me/settings/profile
PATCH /me/settings/security
POST /billing/subscription/change-plan
GET /admin/users
PATCH /admin/users/{id}/status
PATCH /author/users/{id}/role
GET /author/dashboard

---

# MOBILE APPLICATION

Technology:

Flutter + Dart

Responsibilities:

voice recording
UI
memory confirmation
display answers
dashboard visualization
authentication

Main screens:

Home
Memory recording
Question recording
Dashboard
Memory list
Settings
Admin user management (admin/author role)
Author supervision dashboard (author role only)

---

# LANGUAGE AND NAMING POLICY

Official product language is English.

Codebase conventions:

function names
component names
API field names
comments
logs

must be written in English.

---

# MVP BRANDING

App display name:

Personal AI Assistant

Logo policy:

use a placeholder logo in MVP until final brand assets are defined.

---

# BACKEND

Technology:

Python FastAPI

Responsibilities:

API endpoints
AI orchestration
database access
memory processing
receipt photo uploads only

---

# STORAGE

Files are stored in cloud object storage.

Examples:

Supabase Storage

The database stores file URLs.

---

# AUTHENTICATION

Authentication is handled by Supabase Auth.

The backend validates tokens from the provider.

Authorization model:

roles:
user
admin
author

Role naming note:

`subscriber` in product language maps to technical role `user`.

account status:
active
suspended
canceled

Suspended users must not access protected product flows until reactivated.
Canceled users must not access protected product flows unless reactivated by policy.

Role hierarchy:

author > admin > user

`author` inherits admin capabilities and can also update user roles (`user` <-> `admin`).

---

# BILLING

Billing handled by Stripe.

Responsibilities:

subscription management
payments
billing events
plan upgrades
plan downgrades

Users must be able to manage subscription in app settings (`free` <-> `premium`) according to billing policy.

Role-based billing policy:

- `admin` and `author` are always `premium`
- `admin` and `author` are billing-exempt (no payment required)
- role promotion to `admin`/`author` auto-enforces `premium` + billing exemption
- role demotion to `user` removes billing exemption and returns to normal user billing policy

---

# ACCOUNT SETTINGS

Users must have a settings screen to manage:

profile data
email change flow
password change flow
subscription plan and billing status

All sensitive changes must trigger transactional notifications.

---

# ADMIN CAPABILITIES

Admin users must have a dedicated management surface with:

user list
search/filter
account status actions (suspend/reactivate/cancel)

Admin actions must be audited and protected by role-based access control.

---

# AUTHOR CAPABILITIES

Author is the highest privileged role.

Author must have:

all admin capabilities
ability to promote/demote user roles (`user` <-> `admin`)
global supervision dashboard with cross-app metrics (users, plans, operational health, usage)

Author actions must be strictly audited.

Author safety policy (mandatory):

- author cannot change own role
- author cannot suspend/cancel own account
- system must always keep at least one active author
- operations that would remove the last active author must be rejected
- all role/status changes by author require explicit audit trail

---

# TRANSACTIONAL NOTIFICATIONS

The system must send automatic notifications for critical account/billing/security events:

email change
password change
account suspension/reactivation
plan change
billing issues

Email provider choice is intentionally left open (to be selected separately).

---

# PRODUCT POSITIONING

Product type:

Memory Assistant

Not a general AI chatbot.

Focus:

life tracking
object tracking
expense tracking
loan tracking
personal memory

---

# FREE PLAN

Basic memory storage
Voice input
Question answering
Limited AI usage

Example limits:

100 memories
50 questions per month

---

# PREMIUM PLAN

Price range:

10-15 EUR per month

Features:

unlimited memories
receipt photo attachments
advanced insights
priority AI processing

---

# FUTURE FEATURES

Planned improvements:

proactive reminders
expense insights
smart categorization
multi-device sync
advanced analytics

---

# AI MODEL STRATEGY

Current provider:

OpenAI

Future architecture supports multiple providers.

Possible additions:

Anthropic
local models
other AI services

---

# ARCHITECTURE PRINCIPLES

The system must be:

scalable
modular
cloud-native
AI-ready

Key principles:

stateless backend
external AI services
database-driven calculations
event-based memory model

---

# FINAL NOTE

All architectural and product decisions recorded in this document must be preserved.

No implementation should contradict the decisions defined here.
