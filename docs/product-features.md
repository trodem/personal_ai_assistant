# Product Features

This document defines the product capabilities of the Personal AI Assistant.

The application is designed as a **Memory Assistant** that helps users store, retrieve, and reason over personal information.

The system focuses on **real-world information tracking**, not general AI conversation.

---

# Core Concept

The assistant acts as a **second brain** for the user.

Users can:

* store information via voice
* ask questions about their past actions
* track objects, expenses, and loans
* retrieve notes and receipt photos linked to memories
* receive summaries and insights

The assistant remembers events and reconstructs state when answering questions.

---

# Core User Actions

The application has two primary actions:

### Add Memory

Users record voice input describing something that happened.

Examples:

"I put four boxes of peas in the cellar."

"I lent Marco 200 francs."

"I bought motorcycle oil for 45 francs."

The assistant extracts structured information and asks for confirmation before saving.

---

### Ask Assistant

Users ask questions about their stored memories.

Examples:

"How much did I spend on the motorcycle last year?"

"Who owes me money?"

"How many peas are left in the cellar?"

The assistant retrieves relevant data and generates a natural response.

---

# Memory Types

The system stores memories using canonical categories:

expense_event
inventory_event
loan_event
note
document

User language such as "purchase", "object tracking", or generic "event" is interpreted as intent and mapped to one canonical type.

Some memories represent events that modify a state over time.

---

# Event-Based Tracking

Certain memories represent state changes.

Examples:

Inventory
Loans
Counters

Example:

User:

"I put four boxes of peas in the cellar."

Later:

"I took two boxes."

The assistant computes the current state dynamically.

---

# Attachments

Memories may include files such as:

Photos
Receipts
Receipt photos only (no PDF/documents/contracts in MVP)

Files are stored in cloud storage and linked to the memory record.

---

# Dashboard

Users can view a dashboard summarizing their data.

Examples:

Total expenses
Recent memories
Inventory summaries
Outstanding loans

Future versions may include visual charts and statistics.

---

# User Settings

Users must have a settings area for:

Profile update
Email/password security actions
Subscription management (`free`/`premium`)

Sensitive changes must trigger transactional notifications.

---

# Admin Panel

Admin users must have a management interface for:

User list with search/filter
Account status control (`suspend`/`reactivate`/`cancel`)
Operational user oversight

Admin actions require strict role checks and audit logging.

`Admin` accounts are always `premium` and billing-exempt by role policy.

---

# Author Panel

Author users (highest role) must have:

All admin capabilities
Role management (`user` <-> `admin`)
Global supervision dashboard (user stats, plan distribution, operational KPIs, risk signals)

Author actions require strict audit and access controls.

`Author` accounts are always `premium` and billing-exempt by role policy.

---

# Voice Interaction

Voice is the primary input method.

Interaction model:

Push-to-talk recording

The user records a voice message and sends it to the assistant.

The assistant processes the message and responds.

---

# Free Plan

Basic memory storage
Voice input
Question answering
Limited monthly usage

---

# Premium Plan

Unlimited memories
Receipt photo attachments
Advanced analytics
Priority AI processing
Extended history

---

# Business Use Cases

The assistant can also be used by professionals.

Examples:

Technicians tracking repairs
Freelancers tracking expenses
Small businesses tracking tools or inventory

---

# Future Features

Planned future improvements include:

Proactive reminders
Expense insights
Smart categorization improvements
Multi-device synchronization
Advanced reporting
