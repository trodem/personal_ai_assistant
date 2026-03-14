# AI UX Contract

## Purpose

Define explicit UX rules for AI-driven interactions in the app.

This contract ensures consistency, trust, and predictable user behavior.

---

## Scope

Applies to:

- memory capture flow
- clarification flow
- confirmation flow
- question/answer flow
- receipt OCR proposal flow

---

## Core UX Principles

- never auto-save user memories
- always show what the assistant understood before persistence
- ask one clarification question per turn
- keep user control with explicit actions (`Confirm`, `Modify`, `Cancel`)
- separate facts from confidence/uncertainty

---

## Chat Surface Contract

The AI interaction surface must be chat-style with bottom composer:

- text input
- microphone button
- send button
- attachment button (receipt photos only)

Composer behavior:

- disable send when input is empty
- show upload/transcription processing state inline
- show retry action on transient failures

---

## Clarification UX Contract

- ask one missing required field at a time
- questions must be concise and specific
- if user replies "unknown", capture as explicit unknown when policy allows
- stop clarification when required fields are complete

Error prevention:

- do not ask duplicate clarifications for already-confirmed fields
- do not continue clarification after user cancels

---

## Confirmation UX Contract

Before persistence, show a structured summary:

- memory type
- key extracted fields
- absolute editable datetime (`YYYY-MM-DD HH:mm`)
- source context (voice/text/receipt OCR)

Required actions:

- `Confirm`
- `Modify`
- `Cancel`

No hidden persistence is allowed before `Confirm`.

---

## Modify UX Contract

- default to guided field editor by memory type
- avoid raw JSON editing as primary mode
- preserve unchanged fields
- re-run validation before allowing confirm

---

## Question Answer UX Contract

Answer presentation:

- concise natural-language answer first
- expandable "Why this answer" section with:
- confidence (`high`/`medium`/`low`)
- source memory references
- short explanation of applied filters

No-result behavior:

- explicit "no data found"
- CTA to add memory

Ambiguity behavior:

- ask clarification before final answer

---

## Receipt/OCR UX Contract

- show upload progress
- show OCR processing state
- show extracted proposal preview
- never save memory automatically from scan
- preserve same `Confirm/Modify/Cancel` pattern as voice/text memory

Failure behavior:

- show user-friendly error with retry action
- keep failure reason machine-readable in backend error code

---

## State and Feedback Contract

Every AI action must expose visible state:

- `idle`
- `processing`
- `needs_clarification`
- `ready_to_confirm`
- `saved`
- `failed`

UI must avoid silent transitions.

---

## Error UX Contract

- map backend errors to actionable user messages
- show retry only when `retryable=true`
- for auth/permission errors, show recovery path (login/re-auth/settings)
- for validation errors, focus user on missing/invalid fields

Error semantics must align with `docs/error-model.md`.

---

## Accessibility and Inclusion

- all action buttons must be reachable with screen readers
- voice and text paths must both allow full completion of critical flows
- color is not the only carrier of status/meaning
- dynamic type support must not truncate confirmation-critical fields

---

## Localization Rules

- all microcopy must support MVP locales (`en`, `it`, `de`)
- fallback language is `en`
- no mixed-language UI fragments unless explicitly requested

---

## Telemetry Hooks

UX-critical events must be tracked per `docs/product-analytics.md`:

- onboarding progression
- clarification loops
- confirm/modify/cancel outcomes
- no-result and ambiguity frequency
- retry/failure interactions

---

## Governance

- any UX behavior change in AI flows must update this document
- related updates must stay aligned across `TODO.md`, architecture docs, and API/error contracts
