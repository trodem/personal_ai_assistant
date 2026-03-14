# Model and Prompt Registry

## Purpose

Define the canonical mapping between AI use-cases, model versions, and prompt versions.

This prevents silent model changes and guarantees reproducible behavior.

---

## Scope

This registry is required for:

- transcription (voice-to-text)
- memory extraction
- clarification assistant turns
- question answering phrasing
- embedding generation

---

## Registry Rules

- every AI use-case must have one active registry entry
- model changes require registry update and changelog update in the same iteration
- prompt changes require explicit prompt version bump
- production rollout must support rollback to previous stable entry
- deprecated entries remain documented for auditability

---

## Registry Schema

Each entry must define:

- `use_case`
- `provider`
- `model_id`
- `model_version`
- `prompt_spec`
- `prompt_version`
- `temperature`
- `max_tokens`
- `fallback_entry`
- `rollout_stage` (`dev`, `staging`, `prod_canary`, `prod_full`)
- `owner`
- `last_validated_at`

---

## Initial Entries (MVP Baseline)

1. `voice_transcription`
- provider: `openai`
- model_id: `whisper-1` (or approved successor)
- prompt_spec: `n/a`

2. `memory_extraction`
- provider: `openai`
- model_id: `gpt-*` (exact ID locked per environment)
- prompt_spec: `specs/memory-extraction.md`
- prompt_version: `v1`

3. `clarification_generation`
- provider: `openai`
- model_id: `gpt-*` (cost-efficient tier)
- prompt_spec: `specs/memory-extraction.md` (clarification section)
- prompt_version: `v1`

4. `question_response_nlg`
- provider: `openai`
- model_id: `gpt-*` (cost-efficient default, escalated for complex cases)
- prompt_spec: internal query response template
- prompt_version: `v1`

5. `embedding_generation`
- provider: `openai`
- model_id: `text-embedding-*`
- prompt_spec: `n/a`

---

## Rollout and Rollback Policy

- `dev` validation must pass before `staging`
- `staging` must pass contract, regression, and cost checks before `prod_canary`
- `prod_canary` rollout uses limited traffic percentage with error/cost guardrails
- rollback must switch to `fallback_entry` immediately on regression/cost spike/provider instability

---

## Validation Gates

Before promoting an entry:

- functional regression checks pass
- extraction/query quality checks pass
- cost delta is within approved threshold
- latency delta is within approved threshold
- no unresolved security/compliance concern

---

## Governance

- this file is authoritative for model/prompt versions
- changes must be synchronized with:
- `docs/ai-cost-control.md`
- `TODO.md`
- `CHANGELOG.md`
