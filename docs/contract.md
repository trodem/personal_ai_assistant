# Personal AI Assistant Memory Contract

## Overview

The Personal AI Assistant stores user information as structured memories.

Memories are created through an AI-assisted extraction process and must be confirmed by the user before being saved.

The system prioritizes accuracy, user control, and data clarity.

---

# Memory Creation Flow

Memory creation follows an interactive process.

1. User provides input (voice or text)
2. AI analyzes the content
3. AI extracts structured information
4. If information is incomplete, the assistant asks clarification questions
5. The assistant summarizes the extracted data
6. The user confirms, modifies, or cancels the memory
7. The memory is stored

---

# Frontend Interaction Contract (Memory Capture)

Memory capture must use a chat-style interface.

Input composer (bottom of screen) must include:

- text input box
- microphone button
- send button
- attachment button

New memory flow:

1. user starts a new input
2. user can type or record voice
3. user can add attachments from the same composer flow
4. assistant asks one clarification question at a time
5. assistant shows final summary with actions: `Confirm`, `Modify`, `Cancel`

`Save as draft` is not part of MVP.

Attachment policy in MVP:

- only receipt photos are allowed as attachments
- allowed formats: `jpg`, `jpeg`, `png`, `webp`, `heic`
- PDF and any non-image file must be rejected with validation error

---

# Example Flow

User input:

"I bought bread yesterday."

Assistant:

"Where did you buy the bread?"
"How much did you pay?"

User response:

"At Coop, 3 CHF."

Assistant summary:

Type: expense_event  
Item: bread  
Location: Coop  
Amount: 3 CHF  
Date: yesterday  

User options:

Confirm  
Modify  
Cancel

Only confirmed memories are stored.

---

# Memory Structure

Each memory contains:

- raw user input
- memory type
- structured extracted data
- embeddings for semantic search
- creation timestamp

Example:
{
"memory_type": "expense_event",
"item": "bread",
"location": "Coop",
"amount": 3,
"currency": "CHF"
}


---

# Memory Editing

Users can modify existing memories.

Example:

User:

"The amount was 120, not 100."

The system updates the memory while keeping version history internally.

---

# Memory Deletion

Users can delete individual memories.

Deletion can occur through:

UI interaction (delete button)

or natural language:

"Delete the information about the bread."

The system identifies the correct memory and removes it.

---

# AI Clarification

If the system detects incomplete information, the assistant must ask follow-up questions before saving.

Example:

Input:

"I bought bread."

Clarification:

Where did you buy it?  
How much did you pay?

Clarification strategy:

- ask one question at a time
- continue until semantic context fields are populated (`who`, `what`, `where`, `when`, `why`, `how`)
- if a value is truly unknown, user may explicitly set "unknown" (non-null)

---

# Data Accuracy Principle

Memories must only be stored after explicit user confirmation.

The system must never save assumptions without validation.

---

# Required-Field Save Rule

Memory persistence is allowed only when required fields for the selected `memory_type` are present.

If required fields are missing:

- the assistant must ask clarification questions
- the system must not persist the memory
- backend should return validation error (`memory.missing_required_fields`) if persistence is attempted

---

# Default Date-Time Rule

If the user does not explicitly provide date/time, `when` must be set to the current timestamp during ingestion.

The default value must be shown in confirmation output so the user can modify it before final save.

The value shown to users must be absolute and editable (format: `YYYY-MM-DD HH:mm`).

Relative time expressions (for example: "today", "yesterday", "last month") must be converted into absolute date/time values before confirmation is shown.

---

# Modify UX Rule

`Modify` must open a guided field editor by memory type (not raw JSON by default).

Optional advanced/raw editing may exist, but guided fields are the primary UX.
