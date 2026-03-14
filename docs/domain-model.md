# Personal AI Assistant Domain Model

## Overview

The Personal AI Assistant stores user information as structured memories.

Each memory contains both:

- the original user text
- structured extracted data

The system uses AI to classify memories and extract relevant fields.

If information is incomplete, the assistant may ask follow-up questions before storing the memory.

---

# Core Entities

## User

Represents a registered application user.

Fields:

- id
- email
- role
- status
- subscription status
- created_at

Role values:

- user
- admin

Status values:

- active
- suspended

---

## Memory

A memory represents a piece of information recorded by the user.

Fields:

- id
- user_id
- raw_text
- memory_type
- structured_data
- embedding
- created_at

---

# Memory Types (Canonical Storage Taxonomy)

All stored memories must use one of these canonical types:

- expense_event
- inventory_event
- loan_event
- note
- document

---

## expense_event

Represents money spent, including user intents such as "purchase" and maintenance costs.

Example:

"I bought shoes in Rome for 25 CHF."

Fields:

- amount
- currency
- item
- location
- action
- when

---

## inventory_event

Represents storing, moving, adding, or removing physical items.

Example:

"I put four boxes of peas in the cellar."

Fields:

- item
- quantity
- location
- action
- when

---

## loan_event

Represents lending and repayment operations.

Example:

"I lent Marco 200 francs."

Fields:

- person
- amount
- currency
- action
- when

---

## note

Generic information saved by the user.

Example:

"Remember that the plumber will come tomorrow."

Fields:

- what
- who
- when
- metadata

---

## document

Memory linked to one or more receipt photo attachments.

Example:

"Store this receipt photo for the motorcycle repair."

Fields:

- what
- where
- when
- metadata

---

## Intent Mapping

User language can express intents such as "purchase", "object tracking", or "event".
These intents are normalized by extraction logic into canonical storage types.

---

# AI Extraction Pipeline

When the user records information:

1. voice or text input is received
2. AI analyzes the content
3. memory type is determined
4. structured fields are extracted
5. if required data is missing, the assistant asks follow-up questions
6. memory is stored after explicit user confirmation
7. embeddings are generated for semantic search

---

# Query Model

When a user asks a question:

1. the query is converted to an embedding
2. relevant memories are retrieved using vector search
3. structured data may be aggregated in backend/database
4. the AI generates the final natural-language answer

---

## Event-Based Memories

Some memories represent events that modify a state over time.

Instead of storing only the final state, the system stores events and computes state dynamically.

### Inventory Events

Example:

"I put four boxes of peas in the cellar."
{
"memory_type": "inventory_event",
"item": "peas",
"location": "cellar",
"quantity": 4,
"action": "add"
}

Example:

"I took two boxes of peas from the cellar."
{
"memory_type": "inventory_event",
"item": "peas",
"location": "cellar",
"quantity": 2,
"action": "remove"
}

### Loan Events

Example:

"I lent Marco 200 francs."
{
"memory_type": "loan_event",
"person": "Marco",
"amount": 200,
"currency": "CHF",
"action": "lend"
}

Example:

"Marco returned 50 francs."
{
"memory_type": "loan_event",
"person": "Marco",
"amount": 50,
"currency": "CHF",
"action": "repay"
}
