# Personal AI Assistant Architecture

## Overview

Personal AI Assistant is a voice-first mobile application that allows users to store personal information and query it later using natural language.

The system is composed of:

- a mobile application
- a backend API
- AI processing services
- a cloud database
- object storage for receipt-photo attachments

The architecture is designed to be scalable, secure, and AI-native.

---

# System Components

## Mobile Application

Technology:
Flutter / Dart

Responsibilities:

- user interface
- voice recording
- sending requests to backend
- displaying AI answers
- showing dashboard insights
- receipt photo capture/selection

Supported inputs:

- voice
- text
- receipt photos (camera/gallery attachment flow)

---

## Backend API

Technology:
Python + FastAPI

Responsibilities:

- user authentication validation
- request processing
- memory extraction
- receipt-photo validation and upload
- OCR pipeline orchestration
- attachment lifecycle state handling
- AI orchestration
- embeddings generation
- semantic search
- analytics

The backend exposes REST APIs used by the mobile application.

---

## Authentication

Authentication is handled by an external provider.

Provider:
Supabase Auth

Flow:

User login -> Supabase Auth -> JWT token -> Backend verification

The backend validates tokens before processing requests.

---

## AI Processing

AI is used for:

- extracting structured information from user input
- OCR text interpretation for receipt photos
- generating embeddings
- answering user queries
- generating insights

Provider (initial):

OpenAI

The architecture is designed to support multiple AI providers in the future.

---

## Speech Processing

Voice input is converted to text using:

OpenAI Whisper API

Flow:

User voice -> mobile recording -> backend -> Whisper API -> text

---

## Database

Primary database:

PostgreSQL

Provider:
Supabase Postgres

The database stores:

- users
- memories
- extracted structured data
- attachments and OCR/lifecycle metadata
- analytics data

---

## Vector Search

Semantic search is implemented using:

pgvector (PostgreSQL extension)

Embeddings are generated from stored memories and used to retrieve relevant information when the user asks questions.

---

## Memory Pipeline

The memory pipeline works as follows:

User input (voice or text)

-> speech-to-text conversion (for voice)

-> memory extraction

-> clarification (if required)

-> user confirmation (`Confirm / Modify / Cancel`)

-> storage in PostgreSQL

-> embeddings generation / vector indexing

Memories must never be saved automatically without explicit user confirmation.

When a user asks a question:

query -> embedding -> vector search -> relevant memories -> AI response generation

---

## Receipt Attachment Pipeline

Receipt-photo ingestion works as follows:

receipt photo (camera or gallery)

-> strict file validation (`jpg`, `jpeg`, `png`, `webp`, `heic`)

-> Supabase Storage upload

-> OCR extraction

-> memory proposal generation

-> clarification (if required)

-> user confirmation (`Confirm / Modify / Cancel`)

-> memory persistence

Upload/scan alone must not persist memory.

Attachment lifecycle states:

- uploaded
- ocr_processing
- proposal_ready
- confirmed or failed

---

## Deployment

The system will be deployed in a cloud environment.

Components:

- mobile application
- backend API
- Supabase Postgres
- Supabase Storage
- AI services

The backend will run inside containers and can scale horizontally.

---

## Key Principles

Voice-first interaction

AI-native architecture

Cloud-based memory storage

Secure authentication

Scalable backend design

Database-first calculations

Explicit user confirmation before persistence

---

## Event-Based State Computation

Certain types of memories represent events that modify a state.

Examples include:

- inventory changes
- loans and repayments
- cumulative expenses

The system stores individual events and computes the current state dynamically when answering user queries.
