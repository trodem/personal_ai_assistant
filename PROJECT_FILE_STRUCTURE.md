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
settings.py
admin.py
author.py
billing.py
notifications.py

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

settings/

profile_service.py
security_service.py
notification_preferences_service.py
payment_methods_service.py

admin/

user_admin_service.py

author/

author_supervision_service.py
role_management_service.py

billing/

billing_service.py

notifications/

notification_service.py
push_provider_adapter.py
email_provider_adapter.py

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

POST /api/v1/voice/memory
POST /api/v1/voice/question

memory.py

POST /api/v1/memory
DELETE /api/v1/memory/{id}

query.py

GET /api/v1/memories
POST /api/v1/question
POST /api/v1/question/stream

attachments.py

POST /api/v1/attachments

dashboard.py

GET /api/v1/dashboard

settings.py

GET /api/v1/me/settings
PATCH /api/v1/me/settings/profile
PATCH /api/v1/me/settings/security
PATCH /api/v1/me/settings/notifications
GET /api/v1/me/settings/payment-methods
POST /api/v1/me/settings/payment-methods/setup-intent
POST /api/v1/me/settings/payment-methods/{id}/default
DELETE /api/v1/me/settings/payment-methods/{id}

notifications.py

GET /api/v1/notifications
POST /api/v1/notifications/{id}/read

admin.py

GET /api/v1/admin/users
PATCH /api/v1/admin/users/{id}/status

author.py

GET /api/v1/author/dashboard
PATCH /api/v1/author/users/{id}/role

billing.py

POST /api/v1/billing/subscription/change-plan

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
product-analytics.md
model-registry.md
ai-ux-contract.md
llmops-dashboard-spec.md
content-moderation.md
data-sanitization.md

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
