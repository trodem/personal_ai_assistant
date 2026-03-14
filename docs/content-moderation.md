# Content Moderation Policy

## Purpose

Define moderation controls for unsafe, abusive, or dangerous content across user inputs and AI outputs.

---

## Scope

Applies to:

- text input
- voice-transcribed text
- OCR-extracted text from receipt images
- AI-generated responses

---

## Moderation Stages

1. Pre-processing moderation (before LLM call)
2. Post-generation moderation (before response shown to user)
3. Audit logging of moderation decisions

---

## Categories (MVP)

- self-harm or violent harm instructions
- illegal activity instructions
- explicit abuse/harassment
- malicious security misuse instructions
- severe sexual content (non-product-related)

---

## Decision Modes

- `allow`: proceed normally
- `warn`: proceed with safety warning
- `block`: deny processing/response and return safe fallback message
- `review`: flag for manual operational review (if enabled)

---

## Product Rules

- moderation checks must run before question-answering generation
- moderation checks must run before memory persistence when unsafe payload is detected
- blocked content must never be sent to downstream AI generation path
- moderation decisions must be deterministic and logged with reason codes

---

## User Experience Rules

- blocked responses must be clear and non-judgmental
- do not reveal internal moderation model details
- provide user-safe next step when possible

---

## Error and Event Mapping

Error codes (see `docs/error-model.md`):

- `moderation.blocked_content`
- `moderation.review_required`

Analytics events (see `docs/product-analytics.md`):

- `moderation_blocked`
- `moderation_warned`
- `moderation_review_flagged`

---

## Governance

- moderation threshold/policy changes must update this file and `CHANGELOG.md`
- all moderation changes must be aligned with `docs/security-threat-model.md`
