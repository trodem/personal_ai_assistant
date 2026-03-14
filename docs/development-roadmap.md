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

* Setup PostgreSQL
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

Deliverable:

Voice memory processing working end-to-end.

---

# Phase 4 - API Endpoints

Goal: Build backend APIs.

Endpoints:

POST /voice/memory
POST /voice/question
POST /memory
GET /memories
DELETE /memory/{id}
POST /attachments
GET /dashboard

Deliverable:

Complete backend API.

---

# Phase 5 - Authentication

Goal: Secure user access.

Tasks:

* Integrate external authentication provider
* Validate tokens in backend
* Connect users to database records

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

* Implement object storage integration
* Upload receipt photos (`jpg`, `jpeg`, `png`, `webp`, `heic`)
* Reject PDF and any non-image upload
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

Deliverable:

Freemium model working.

---

# Phase 11 - Production Preparation

Goal: Prepare for deployment.

Tasks:

* Dockerize backend
* Configure environment secrets
* Setup monitoring
* Setup deployment pipeline

Deliverable:

Production-ready system.
