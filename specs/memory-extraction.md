# Memory Extraction Specification

## Overview

The Personal AI Assistant converts user input into structured memories.

Users may provide input via:

- voice
- text

The system extracts structured data using an AI model.

Memories must always be confirmed by the user before being saved.

---

# Input Types

User input can include:

- expense events
- inventory events
- loan events
- notes
- receipt documents (captured as photos)
- maintenance activities

User wording like "purchase", "store object", or "event" is treated as intent text and mapped to canonical memory types.

The AI model must classify the memory into the correct type.

Allowed canonical `memory_type` values:

- expense_event
- inventory_event
- loan_event
- note
- document

---

# Memory Structure

Each memory contains the following fields.

Core fields:

- memory_id
- user_id
- memory_type
- raw_text
- structured_data
- attachments
- embedding
- created_at
- updated_at

---

# Required Fields by Memory Type (minimum save contract)

The assistant may extract partial data first, but persistence is allowed only when required fields for the detected `memory_type` are present.

- expense_event:
- required: `what` or `item`, `amount`, `currency`

- inventory_event:
- required: `item`, `quantity`, `action`

- loan_event:
- required: `person`, `amount`, `currency`, `action`

- note:
- required: `what`

- document:
- required: `what`
- at least one attachment linked before final save

If required fields are missing, the assistant must continue clarification and must not persist the memory.

---

# Semantic Context Fields

The AI must attempt to extract the following semantic fields when possible.

who  
who is involved

what  
the main action or object

where  
location of the event

when  
date or time

why  
reason or purpose

how  
method or description of the action

---

# Timestamp Default Rule (`when`)

If the user does not explicitly provide a date/time, the system must set `when` to the current timestamp at ingestion time.

If the user later corrects the time, the memory must be updated through the normal confirmation/edit flow.

If the user provides a relative date/time expression (for example: "today", "yesterday", "last week"), the system must normalize it to an absolute date/time before confirmation and persistence.

---

# Example

User input:

"I spent 150 francs on the motorcycle."

AI extraction:

{
"memory_type": "expense_event",
"raw_text": "I spent 150 francs on the motorcycle",
"who": "user",
"what": "motorcycle expense",
"where": null,
"when": "today",
"why": "motorcycle maintenance",
"how": null,
"amount": 150,
"currency": "CHF",
"item": "motorcycle"
}


---

# Clarification Process

If required information is missing, the assistant must ask follow-up questions.

Example:

User input:

"I bought bread."

Assistant:

Where did you buy it?  
How much did you pay?

After clarification, the assistant summarizes the memory before saving.

---

# Confirmation Rule

Memories must never be stored automatically.

The assistant must show the extracted data to the user.

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

# Attachments

Memories may include attachments only as receipt photos.

- photos
- receipts (photo format)

Attachments are stored in cloud object storage and linked to the memory record.

Upload validation must allow only: `jpg`, `jpeg`, `png`, `webp`, `heic`.

PDF and other non-image files must be rejected.

---

# Embeddings

Each memory must generate an embedding vector.

Embeddings are used for semantic search.

The vector is stored using pgvector in PostgreSQL.

---

# Query Pipeline

When the user asks a question:

1. the query is converted to an embedding
2. relevant memories are retrieved using vector search
3. structured data is aggregated when needed
4. the AI generates a final answer
