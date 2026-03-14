# PROJECT BOOTSTRAP

This file instructs the AI agent how to start working on the Personal AI Assistant project.

The agent must follow these rules strictly.

---

# STEP 1 â€” READ PROJECT CONTEXT

Before performing any action the agent must read:

PROJECT_CONTEXT.md

This file contains the entire system specification.

No architectural decision may be ignored.

---

# STEP 2 â€” CONFIRM UNDERSTANDING

After reading the context, the agent must summarize:

System architecture
AI pipeline
Database schema
Memory model
Product positioning

Only after confirming understanding may implementation begin.

---

# STEP 3 â€” IMPLEMENTATION PRIORITY

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

# STEP 4 â€” BACKEND FOUNDATION

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

# STEP 5 â€” DATABASE SETUP

Database:

PostgreSQL

Required extension:

pgvector

Tables:

users
memories
memory_versions
attachments
embeddings

---

# STEP 6 â€” AI PIPELINE IMPLEMENTATION

The AI pipeline must implement:

Speech-to-text using Whisper
Memory extraction using LLM
Clarification system
Confirmation system
Question answering pipeline

AI must never perform calculations.

All calculations must be performed in the backend.

---

# STEP 7 â€” API IMPLEMENTATION

Required endpoints:

POST /voice/memory
POST /voice/question
POST /memory
GET /memories
DELETE /memory/{id}
POST /attachments
GET /dashboard

The API must enforce user authentication.

---

# STEP 8 â€” MOBILE APPLICATION

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

# STEP 9 â€” STORAGE

Attachments must be stored in cloud object storage.

MVP attachment policy:

- only receipt photos are allowed (jpg, jpeg, png, webp, heic)
- PDF and non-image files must be rejected
- upload/scan alone must never persist memory
- OCR output must go through normal clarification + confirmation flow

Recommended providers:

S3-compatible storage
Cloudflare R2
Supabase storage

The database stores only file metadata.

---

# STEP 10 â€” AUTHENTICATION

Authentication must use an external provider.

Recommended provider:

Clerk

Alternative providers:

Auth0
Supabase Auth

The backend validates authentication tokens.

---

# STEP 11 â€” BILLING

Billing must use Stripe.

Required features:

subscription plans
payment processing
subscription validation

Premium features must require active subscription.

---

# STEP 12 â€” DEVELOPMENT PRINCIPLES

The system must follow these principles:

modular architecture
event-based memory model
database-first calculations
AI only for language reasoning
strict user data isolation

---

# STEP 13 â€” SAFETY RULES

The agent must never:

modify architecture decisions
change memory model
remove confirmation system
allow cross-user data access

All sensitive actions require confirmation.

---

# STEP 14 â€” FUTURE EXTENSIONS

The architecture must allow future support for:

multiple AI providers
local AI models
business accounts
advanced analytics

