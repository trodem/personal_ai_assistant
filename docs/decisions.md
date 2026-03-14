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
↓
Backend upload
↓
Whisper speech-to-text

Speech recognition is not performed locally on the device.

---

# AI Pipeline Architecture

The system uses a **multi-stage AI pipeline**.

Pipeline:

Speech-to-text (Whisper)
↓
Memory extraction (LLM)
↓
Clarification if needed
↓
User confirmation
↓
Database storage

AI is also used for generating natural language responses to questions.

---

# Database Strategy

Database: PostgreSQL

Vector search: pgvector extension.

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

# Roles and Administration

The system supports role-based access:

user
admin

Admin capabilities include user management actions (for example suspend/reactivate), protected by RBAC and audit logging.

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

POST /voice/memory
POST /voice/question

This avoids ambiguity and simplifies backend logic.

---

# Pricing Model

Freemium SaaS model.

Free plan:

limited memories
limited questions

Premium plan:

10–15 € per month

Premium features:

unlimited memories
receipt photo attachments
advanced insights

---

# Long-Term Model Flexibility

The AI architecture is designed to support multiple models.

Initial model provider:

OpenAI

Future support may include:

Anthropic
local models
other providers
