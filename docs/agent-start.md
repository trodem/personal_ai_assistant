# Agent Start Guide

This document instructs the AI agent how to begin working on the Personal AI Assistant project.

The agent must follow these instructions strictly.

---

# Step 1 - Read the Project Context

Before performing any action, the agent must read the following files completely:

PROJECT_ONE_SENTENCE.md
PROJECT_CONTEXT.md
PROJECT_BOOTSTRAP.md
PROJECT_FILE_STRUCTURE.md

These files contain the core vision, architecture, and rules of the project.

---

# Step 2 - Read Technical Documentation

After reading the project context, the agent must read documentation in:

docs/
specs/
ADR/

The agent must use the document routing rules in `docs/AGENTS.md` to decide which files to consult for each task type.

The agent must not ignore any architectural decision defined in these documents.

---

# Step 3 - Confirm Understanding

Before writing code, the agent must summarize:

* system architecture
* AI pipeline
* query contract
* database schema
* memory model
* product positioning

If any part is unclear, the agent must request clarification.

---

# Step 4 - Begin Implementation

Development must follow:

- `docs/development-roadmap.md`
- `TODO.md`

The correct order is:

1. Backend foundation
2. Database schema
3. AI pipeline
4. API endpoints
5. Authentication
6. Mobile application
7. Dashboard
8. Attachments
9. Billing

The agent must never start with UI before backend services exist.

---

# Step 5 - Backend First Rule

The backend must always be implemented before frontend features.

Backend responsibilities:

API endpoints
AI orchestration
database queries
authentication validation

The mobile app must only consume backend APIs.

---

# Step 6 - Architecture Protection

The agent must not modify:

* memory model
* event-based architecture
* database-first query execution
* confirmation system
* user data isolation

These architectural decisions are mandatory.

---

# Step 7 - Implementation Principles

The agent must follow these principles:

modular code structure
clear separation of concerns
scalable architecture
secure data handling

The agent must never introduce unnecessary complexity.

---

# Step 8 - Safety Rules

The agent must enforce the following safety constraints:

Users must only access their own data.

AI must not modify stored data without user confirmation.

Sensitive operations must be validated by the backend.

Attachments must be securely stored.

---

# Step 9 - Milestone Mini-Audit

At the end of each milestone, the agent must run a mini-audit:

- verify implementation/doc/spec alignment
- verify architecture rules are still respected
- verify security and user isolation constraints
- verify API contract alignment for touched endpoints
- document blockers before moving to the next milestone

---

# Step 10 - Future Compatibility

All code must allow future expansion including:

multiple AI providers
local AI models
business user accounts
advanced analytics

The architecture must remain flexible.
