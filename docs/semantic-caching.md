# Semantic Caching Policy

## Purpose

Define how semantic caching is used to reduce AI cost and latency without compromising answer quality.

---

## Scope

Applies to question-answering flows:

- `/api/v1/question`
- `/api/v1/question/stream`
- `/api/v1/voice/question` (after transcription)

---

## Cache Strategy

Cache key dimensions:

- user_id
- normalized query intent
- language (`preferred_language`)
- relevant filter context (date range/currency constraints)

Semantic lookup:

- compute embedding for normalized question
- search nearest previous answered queries in user scope
- reuse cached answer only if similarity >= configured threshold

---

## Safety and Quality Guardrails

- never bypass database-first calculation rules
- cached answer must include provenance-compatible source IDs
- do not reuse cache when required constraints differ (currency, period, entity)
- on low confidence or ambiguity, bypass cache and execute full pipeline

---

## Thresholds and TTL (MVP defaults)

- minimum semantic similarity for cache hit: `0.90`
- default cache TTL: `24h`
- shorter TTL for volatile queries (for example "this month"): `1h`
- cache size and eviction policy must be bounded per user

---

## Invalidation Rules

Invalidate relevant cache entries when:

- user creates/updates/deletes memory affecting answer domain
- billing/plan policy changes query limits behavior
- model/prompt major change invalidates output comparability

---

## Metrics and Alerts

Track:

- cache hit rate
- cache miss rate
- latency delta (cached vs non-cached)
- cost savings estimate
- incorrect-cache fallback count

Metrics should feed `docs/llmops-dashboard-spec.md`.

---

## Governance

- caching logic changes must update this document and `CHANGELOG.md`
- policy must remain aligned with `docs/query-contract.md` and `docs/ai-cost-control.md`
