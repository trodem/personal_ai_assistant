# AI Pipeline

This document defines how AI is used inside the Personal AI Assistant.

The system uses a **multi-stage pipeline** instead of relying on a single AI call.

This improves:

* accuracy
* cost efficiency
* control
* explainability

---

# Core Principle

AI is used for:

* language understanding
* memory extraction
* clarification dialogs
* natural language responses

AI is **not responsible for calculations or state management**.

All numerical operations are handled by the backend and database.

---

# Voice Input Pipeline

When a user records voice input, the following pipeline runs.

```
User Voice
↓
Audio Upload
↓
Speech-to-Text (Whisper)
↓
Text Processing
↓
AI Extraction
↓
Structured Memory
```

The transcription is performed using Whisper.

---

# Receipt Photo Pipeline (Attachments)

When a user adds a receipt photo, the following pipeline runs.

```
Receipt Photo (camera/gallery)
↓
Upload validation (type/size/auth)
↓
Object storage persistence
↓
OCR text extraction
↓
Memory extraction proposal
↓
Clarification (if required)
↓
User confirmation (`Confirm / Modify / Cancel`)
↓
Memory stored
```

Rules:

- scan/upload alone must not persist a memory record
- persistence is allowed only after explicit `Confirm`
- OCR output is treated as candidate text and can be edited via `Modify`
- attachment lifecycle state must be tracked (`uploaded`, `ocr_processing`, `proposal_ready`, `confirmed`, `failed`)
- failed OCR must return a retry path and never auto-save partial/uncertain memory
- uploaded images should be normalized before OCR (orientation/quality) and sensitive EXIF metadata removed before long-term storage

---

# Memory Creation Pipeline

When the user records a new memory:

```
voice
↓
Whisper transcription
↓
LLM memory extraction
↓
structured memory proposal
↓
clarification if required
↓
user confirmation
↓
memory stored
```

Example input:

"I put four boxes of peas in the cellar."

Extracted structure:

```
memory_type: inventory_event
item: peas
quantity: 4
location: cellar
action: add
```

---

# Clarification System

If important information is missing, the AI must ask clarification questions.

Example:

User:

"I bought bread."

Assistant:

Where did you buy it?
How much did you pay?

Once enough information is gathered, the assistant proposes the memory structure.

The user must confirm before storage.

If date/time is not provided by the user, the pipeline sets `when` to current timestamp and shows it in confirmation.

If user time is relative (for example: "yesterday"), the pipeline resolves it to an absolute date/time before confirmation.

Clarification interaction policy:

- one question per turn
- continue until semantic fields (`who`, `what`, `where`, `when`, `why`, `how`) are non-null
- user can explicitly provide "unknown" for unavailable values

---

# Confirmation Rule

Memories are **never saved automatically**.

The assistant always displays the extracted structure:

Example:

Type: expense_event
Item: bread
Location: Coop
Amount: 3 CHF

User options:

Confirm
Modify
Cancel

Only confirmed memories are stored.

---

# Question Answering Pipeline

When a user asks a question:

```
voice question
↓
Whisper transcription
↓
intent detection
↓
database query
↓
result aggregation
↓
LLM generates natural response
```

The AI does not perform calculations.

The backend performs:

* sums
* filters
* aggregations

Example question:

"How much did I spend on the motorcycle last year?"

Process:

1. intent detected → expense summary
2. database query
3. sum calculated
4. AI generates final answer

Example response:

"You spent 720 CHF on the motorcycle last year."

---

# Query Resolution Rules (Deterministic)

For queries with "latest/last" semantics (for example: "last service", "latest expense"):

- backend must apply deterministic ordering: `ORDER BY when DESC`
- backend must return the first match: `LIMIT 1`

For ambiguous queries (multiple plausible entities, e.g. multiple vehicles/services):

- assistant must ask a clarification question before final answer
- if user does not clarify, return partial answer with explicit uncertainty note

If no matching data is found:

- return a standard not-found response in natural language
- avoid fabrication and suggest how to record missing data

---

# Retrieval Priority Rule

Question answering must prefer:

1. structured filters and SQL aggregation (primary path)
2. semantic vector retrieval (fallback/augmentation path)

Vector retrieval must not override explicit structured constraints detected in user intent.

---

# Provenance and Confidence

Every question response should include:

- source memory identifiers used for the answer
- optional confidence indicator when disambiguation or sparse context is involved

# Semantic Search

For open-ended questions the system uses embeddings.

Process:

```
user question
↓
embedding generation
↓
vector search in database
↓
retrieve relevant memories
↓
AI answer generation
```

Embeddings are stored using **pgvector**.

---

# Event-Based Reasoning

Inventory, loans, and similar data are stored as events.

Example events:

add inventory
remove inventory
lend money
repay money

The backend reconstructs the current state dynamically.

---

# AI Model Usage

The system currently uses:

* Whisper (speech-to-text)
* OpenAI LLM (language reasoning)

The architecture is designed to support multiple models in the future.

Example:

OpenAI
Anthropic
local models

The AI layer is abstracted so models can be swapped without changing the application logic.

---

# Safety Rules

The AI system must follow strict rules:

* never modify stored data without user confirmation
* never invent financial or inventory data
* always rely on database results for calculations
* ask clarification when information is incomplete

---

# Future Improvements

Planned AI improvements include:

* proactive insights
* automatic categorization improvements
* anomaly detection in expenses
* smart summaries of user activity
