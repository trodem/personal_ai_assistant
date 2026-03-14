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

## Active Registry Entries (MVP Runtime Mapping)

Date of this active mapping: `2026-03-14`

1. `memory_extraction`
- provider: `openai`
- model_id: `gpt-4o-mini`
- model_version: `mvp-v1`
- prompt_spec: `specs/memory-extraction.md`
- prompt_version: `memory_extraction_v1`
- temperature: `0.0`
- max_tokens: `800`
- fallback_entry: `memory_extraction@openai:gpt-4o-mini:mvp-v0:memory_extraction_v0`
- rollout_stage: `dev`
- owner: `backend-team`
- last_validated_at: `2026-03-14`

2. `receipt_ocr_extraction`
- provider: `openai`
- model_id: `gpt-4o-mini`
- model_version: `mvp-v1`
- prompt_spec: `specs/memory-extraction.md`
- prompt_version: `receipt_extraction_v1`
- temperature: `0.0`
- max_tokens: `800`
- fallback_entry: `receipt_ocr_extraction@openai:gpt-4o-mini:mvp-v0:receipt_extraction_v0`
- rollout_stage: `dev`
- owner: `backend-team`
- last_validated_at: `2026-03-14`

3. `answer_generation`
- provider: `openai`
- model_id: `gpt-4o-mini`
- model_version: `mvp-v1`
- prompt_spec: `docs/query-contract.md`
- prompt_version: `answer_generation_v1`
- temperature: `0.2`
- max_tokens: `600`
- fallback_entry: `answer_generation@openai:gpt-4o-mini:mvp-v0:answer_generation_v0`
- rollout_stage: `dev`
- owner: `backend-team`
- last_validated_at: `2026-03-14`

4. `voice_transcription` (planned baseline, not yet active in runtime telemetry)
- provider: `openai`
- model_id: `whisper-1` (or approved successor)
- model_version: `mvp-v1`
- prompt_spec: `n/a`
- prompt_version: `n/a`
- temperature: `n/a`
- max_tokens: `n/a`
- fallback_entry: `voice_transcription@openai:whisper-1:mvp-v0:n/a`
- rollout_stage: `planned`
- owner: `backend-team`
- last_validated_at: `pending`

5. `embedding_generation` (planned baseline, not yet active in runtime telemetry)
- provider: `openai`
- model_id: `text-embedding-*`
- model_version: `mvp-v1`
- prompt_spec: `n/a`
- prompt_version: `n/a`
- temperature: `n/a`
- max_tokens: `n/a`
- fallback_entry: `embedding_generation@openai:text-embedding-*:mvp-v0:n/a`
- rollout_stage: `planned`
- owner: `backend-team`
- last_validated_at: `pending`

## Rollback Entries (Immediate Use)

- `memory_extraction@openai:gpt-4o-mini:mvp-v0:memory_extraction_v0`
- `receipt_ocr_extraction@openai:gpt-4o-mini:mvp-v0:receipt_extraction_v0`
- `answer_generation@openai:gpt-4o-mini:mvp-v0:answer_generation_v0`

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
