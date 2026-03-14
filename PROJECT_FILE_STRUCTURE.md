# PROJECT FILE STRUCTURE

This document defines the directory structure of the Personal AI Assistant project.

The goal is to ensure the project remains organized and scalable.

The repository is divided into three main parts:

* mobile application
* backend services
* documentation and specifications

---

# Root Structure

project-root/

mobile/
backend/
docs/
specs/
infra/

README.md
PROJECT_CONTEXT.md
PROJECT_BOOTSTRAP.md

---

# Mobile Application

mobile/

Technology:

Flutter + Dart

Structure:

mobile/

lib/
main.dart

app/
router.dart
theme.dart

features/

memory/
voice_input/
ask_assistant/
dashboard/
attachments/

services/

api_client.dart
auth_service.dart
voice_service.dart

models/

memory.dart
memory_event.dart
attachment.dart

widgets/

record_button.dart
memory_card.dart

---

# Backend

backend/

Technology:

Python FastAPI

Structure:

backend/

app/

main.py
config.py

api/

voice.py
memory.py
query.py
attachments.py
dashboard.py

services/

ai_pipeline.py
memory_extractor.py
intent_detector.py
vector_search.py

models/

user.py
memory.py
memory_version.py
attachment.py

database/

db.py
migrations/

auth/

auth_middleware.py

utils/

validators.py
logger.py

---

# AI Pipeline

backend/app/services/

ai_pipeline.py

Responsibilities:

speech-to-text orchestration
memory extraction
clarification system
response generation

---

# Database Layer

backend/app/database/

db.py

Handles:

PostgreSQL connection
pgvector support
database session management

---

# API Endpoints

backend/app/api/

voice.py

POST /voice/memory
POST /voice/question

memory.py

POST /memory
DELETE /memory/{id}

query.py

GET /memories

attachments.py

POST /attachments

dashboard.py

GET /dashboard

---

# Documentation

docs/

architecture.md
system-architecture.md
domain-model.md
database-schema.md
ai-pipeline.md
product-features.md
monetization.md
decisions.md

---

# Specifications

specs/

api.yaml
memory-extraction.md

---

# Infrastructure

infra/

docker/
docker-compose.yml

deployment/

scripts/

---

# Future Additions

Future infrastructure components may include:

background job workers
analytics pipeline
AI routing layer
multi-region deployments

The architecture must remain modular to allow these additions.
