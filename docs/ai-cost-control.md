# AI Cost Control Strategy

This document defines how the Personal AI Assistant controls AI usage costs.

AI models are powerful but can become expensive if not managed carefully.

The system must use AI only when necessary.

---

# Core Principle

The assistant must follow a **database-first architecture**.

AI is used only for:

* language understanding
* memory extraction
* natural language responses

AI must not perform:

* numerical calculations
* data filtering
* aggregations

These operations must always be handled by the backend and database.

---

# Efficient Query Execution

When a user asks a question such as:

"How much did I spend on the motorcycle last year?"

The process must be:

1. Detect intent
2. Execute database query
3. Calculate result
4. Use AI only to generate the final natural response

Example:

"You spent 720 CHF on the motorcycle last year."

The AI is not involved in the calculation.

---

# AI Usage Points

AI is used in three main situations.

## Memory Extraction

When the user records a voice memory.

Pipeline:

voice
->
transcription
->
LLM extraction
->
structured memory

This step uses minimal tokens.

---

## Clarification Dialog

If information is incomplete the AI may ask follow-up questions.

Example:

User:

"I bought bread."

Assistant asks:

Where did you buy it?
How much did you pay?

Clarification loops must be short to control costs.

---

## Natural Language Response

AI is used to generate natural responses after the backend has calculated results.

Example:

Database result:

total_expense = 720 CHF

AI response:

"You spent 720 CHF on the motorcycle last year."

---

# Embedding Usage

Vector embeddings are used for semantic search.

Embeddings must be generated only when:

* a new memory is created
* memory content changes

Embeddings must not be regenerated unnecessarily.

---

# Rate Limiting

Free users must have strict limits.

Example limits:

50 questions per month
100 memories

Premium users may have higher limits.

---

# Caching

Frequently asked queries should be cached.

Example:

recent dashboard summaries
recent memory queries

Caching reduces repeated AI calls.

Semantic cache policy and thresholds must follow `docs/semantic-caching.md`.

---

# Token Optimization

Prompts must remain short and structured.

Avoid sending large conversation histories.

Use only the necessary context.

---

# Model Strategy

Initial model provider:

OpenAI

Future architecture must support multiple models.

Possible providers:

Anthropic
local models
other AI APIs

Model routing may allow cost optimization in the future.

Model and prompt version governance must follow `docs/model-registry.md`.

---

# Monitoring

The system must track:

AI request count
token usage
cost per user

Alerts should trigger if usage spikes unexpectedly.

LLMOps dashboard panels and thresholds must follow `docs/llmops-dashboard-spec.md`.

---

# Long-Term Strategy

As the user base grows the system may introduce:

local embedding models
hybrid AI routing
batch processing for analytics

These strategies further reduce AI costs.

---

# Key Principle

AI should enhance the product but must never dominate system cost.

The assistant must remain profitable even with large user growth.
