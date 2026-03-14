# MVP Scope and Non-Goals (Source of Truth)

## Purpose
This document is the single source of truth for MVP scope boundaries.

## In Scope (MVP)
- Voice-first memory capture with explicit confirmation flow (`Confirm/Modify/Cancel`).
- Memory types: `expense_event`, `inventory_event`, `loan_event`, `note`, `document`.
- Question answering over user memories with database-first logic.
- Receipt photo attachments with OCR-assisted proposal flow.
- Mobile app in Flutter with core memory/question flows.
- Backend in FastAPI with Supabase Auth + Postgres (`pgvector`) + Storage.
- Billing baseline with Stripe integration path (`free`/`premium` model).
- Supported languages for MVP: `en`, `it`, `de` with fallback `en`.

## Non-Goals (MVP)
- General-purpose chatbot behavior outside memory-assistant scope.
- Always-on microphone listening.
- Broad file support beyond receipt-photo-centric attachment flow.
- Enterprise multi-tenant operations beyond MVP baseline guardrails.
- Advanced production scaling/HA features beyond defined launch milestones.

## Scope Change Policy
- Any scope or non-goal change requires explicit update of this file and aligned updates in `TODO.md`, relevant docs, and API/contract artifacts when impacted.

## Reference Alignment
- `PROJECT_CONTEXT.md`
- `README.md` (Official MVP Stack)
- `TODO.md` (execution checklist and milestones)
