# Query Contract

## Purpose

Define the supported query behaviors, deterministic rules, fallback behavior, and response shape for user questions.

This document complements:

- `docs/ai-pipeline.md`
- `docs/error-model.md`
- `specs/api.yaml`

---

## Scope

This contract applies to question answering features (`/api/v1/voice/question`, `/api/v1/question`, and `/api/v1/question/stream`).

---

## Supported Query Categories

1. Expense summaries
- examples: "How much did I spend on the motorcycle last year?"

2. Latest/last record lookup
- examples: "How much was my last service?"

3. Loan status
- examples: "Who still owes me money?"

4. Inventory state
- examples: "How many peas are left in the cellar?"

5. Location recall / note retrieval
- examples: "Where did I put my passport?"

---

## Deterministic Rules

### Latest/Last semantics

Queries containing latest/last intent must use:

- `ORDER BY when DESC`
- `LIMIT 1`

### Database-first

Numerical answers must be produced by backend/database logic, never by free-form LLM reasoning.

### Retrieval priority

1. Structured filters + SQL (primary)
2. Semantic vector retrieval (fallback/augmentation)

Semantic cache policy:

- semantic cache may be used only after database-first constraints are preserved
- cache hit requires user-scoped key + similarity threshold from `docs/semantic-caching.md`
- cache must be bypassed for ambiguous intent or changed constraint context

Vector retrieval must not override explicit structured constraints extracted from intent.

### Multi-currency queries

If results include multiple currencies:

- do not silently convert currencies
- aggregate by currency and return separate totals
- if conversion is requested explicitly, require a documented FX policy and rate timestamp

---

## Ambiguity Handling

If query intent maps to multiple plausible entities:

- ask one clarification question first
- do not fabricate a single definitive answer

If user does not clarify:

- return best-effort partial answer with explicit uncertainty
- set lower confidence in response metadata

Error code mapping:

- `query.ambiguous_intent` (see `docs/error-model.md`)

Clarification behavior:

- ask one question at a time in chat-style flow
- continue clarifications until needed disambiguation fields are non-null
- if user explicitly marks a field as unknown, proceed with uncertainty disclosure

---

## No-Result Handling

If no relevant memories are found:

- return a clear not-found answer
- suggest recording the missing information
- do not fabricate facts

Error code mapping:

- `query.no_results` (see `docs/error-model.md`)

---

## Response Contract

Question responses should include:

- `answer` (natural-language output)
- `source_memory_ids` (provenance list)
- `confidence` (`high`/`medium`/`low`)

Language behavior:

- answer language should follow user `preferred_language` when configured
- supported MVP languages: `en`, `it`, `de`
- fallback language is `en`
- response must avoid mixed-language fragments unless user input explicitly requests bilingual output

When multi-currency totals are involved, response should preserve currency separation unless explicit conversion policy is applied.

`source_memory_ids` must reflect the records actually used by the backend for the answer.

Streaming behavior (`/api/v1/question/stream`):

- transport: Server-Sent Events (SSE)
- stream emits incremental `chunk` events and one terminal `done` event
- terminal `done` event must include confidence and provenance fields
- if streaming channel is unavailable, client must fallback to `/api/v1/question`

Frontend presentation recommendation:

- show concise natural-language answer by default
- provide expandable "Why this answer" panel with:
- confidence
- source references
- short explanation of applied filters (when relevant)

---

## Out-of-Scope Query Types (MVP)

- real-time external information (weather, news, markets)
- generic assistant tasks unrelated to stored user memories
- enterprise-integrated analytics requiring external systems

For out-of-scope queries, return a clear boundary message.

---

## No-Result UX Recommendation

When no data is found:

- show a clear not-found answer
- add action prompt to create memory (for example: "Add Memory")
