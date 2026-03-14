# Database Schema

Database: PostgreSQL
Provider: Supabase Postgres
Extensions: pgvector

The database stores all user memories, events, attachments, and AI embeddings.

---

# Users

Stores registered users.

Table: users

Fields:

id (uuid, primary key)
email (text)
role (text)
status (text)
created_at (timestamp)
subscription_plan (text)
billing_exempt (boolean)

Role values:

user
admin
author

Status values:

active
suspended
canceled

---

# Memories

Logical memory container.

Table: memories

Fields:

id (uuid, primary key)
user_id (uuid, foreign key)
memory_type (text)
created_at (timestamp)
updated_at (timestamp)

Memory types:

expense_event
inventory_event
loan_event
note
document

---

# Memory Versions

Stores version history of each memory.

Table: memory_versions

Fields:

id (uuid, primary key)
memory_id (uuid, foreign key)
user_id (uuid, foreign key)
version_number (integer)
raw_text (text)

Typed extracted fields:

item (text)
location (text)
person (text)
action (text)
quantity (integer)
amount (numeric)
currency (text)

Context fields:

who (text)
what (text)
where (text)
when (timestamp)
why (text)
how (text)

metadata (jsonb)

created_at (timestamp)

Only the latest version is considered active.

---

# Attachments

Stores file references linked to memories.

Table: attachments

Fields:

id (uuid, primary key)
memory_id (uuid)
user_id (uuid)
file_url (text)
file_type (text)
storage_key (text)
status (text)
ocr_status (text)
ocr_text (text)
content_hash (text)
error_code (text)
created_at (timestamp)

Files are stored in cloud object storage.

Attachment policy in MVP:

- only receipt photo files are allowed
- allowed formats: `jpg`, `jpeg`, `png`, `webp`, `heic`
- PDF and non-image files are rejected at upload validation
- attachment lifecycle must be tracked in DB for reliability and cleanup

---

# Embeddings

Vector embeddings used for semantic search.

Table: embeddings

Fields:

id (uuid, primary key)
memory_id (uuid)
user_id (uuid)
embedding (vector)
created_at (timestamp)

Extension required:

CREATE EXTENSION vector;

---

# Event-based State

Inventory, loans, and similar records are stored as events.

Example inventory event:

item: peas
location: cellar
quantity: 4
action: add

Example loan event:

person: Marco
amount: 200
action: lend

The system computes the current state dynamically when answering queries.

---

# Multi-user Isolation

All user-scoped tables include `user_id` to isolate user data.

Users cannot access data belonging to other users.

System-owned tables that do not represent user content may omit `user_id`.

---

# AI Query History

Stores persisted question/answer interactions used for export, analytics, and auditability.

Table: qa_interactions

Fields:

id (uuid, primary key)
user_id (uuid, foreign key)
question_text (text)
answer_text (text)
confidence (text)
source_memory_ids (jsonb)
created_at (timestamp)

---

# Attachments Storage

Files are not stored directly in PostgreSQL.

They are uploaded to Supabase Storage.

The database stores only metadata and URLs.
