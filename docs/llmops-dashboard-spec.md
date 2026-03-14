# LLMOps Dashboard Specification

## Purpose

Define required dashboards, metrics, and alert thresholds for AI operations.

This specification standardizes monitoring for cost, quality, latency, and reliability.

---

## Scope

Covers:

- AI request monitoring
- token and cost control
- model/version health
- failure and fallback tracking
- provider dependency status

---

## Required Dashboards

### 1) AI Overview Dashboard

Panels:

- AI requests per minute (RPM)
- success rate (2xx / total AI calls)
- error rate by class (4xx, 5xx, timeout, provider)
- p50/p95/p99 latency per AI use-case
- active model distribution by use-case

---

### 2) Cost Dashboard

Panels:

- daily cost (total and per provider)
- monthly cost burn vs budget
- cost per user (top consumers)
- cost per feature/use-case
- token in/out totals and trend

---

### 3) Quality and UX Dashboard

Panels:

- extraction confirmation rate
- clarification turns per memory flow
- question no-result rate
- ambiguity rate (`query.ambiguous_intent`)
- OCR failure rate and stuck `ocr_processing` count

---

### 4) Reliability Dashboard

Panels:

- dependency failure rate (`openai`, `supabase`, `stripe`)
- circuit breaker open events
- fallback model activation count
- queue retry/dead-letter counts
- rate limit trigger counts

---

## Standard Labels and Dimensions

Every metric should support dimensions:

- `environment` (`dev`, `staging`, `prod`)
- `use_case` (`memory_extraction`, `clarification_generation`, `question_response_nlg`, `voice_transcription`, `embedding_generation`)
- `provider`
- `model_id`
- `model_version`
- `prompt_version`
- `user_plan` (`free`, `premium`)

---

## Alert Thresholds (MVP defaults)

### Reliability

- AI endpoint p95 latency > 12s for 10m -> warning
- AI endpoint p95 latency > 20s for 5m -> critical
- AI 5xx rate > 3% for 5m -> warning
- AI 5xx rate > 8% for 5m -> critical
- provider-specific failure rate > 5% for 10m -> warning

### Cost

- daily spend > 120% of 7-day moving average -> warning
- daily spend > 160% of 7-day moving average -> critical
- monthly budget burn projection > 110% -> warning
- monthly budget burn projection > 130% -> critical

### Quality

- extraction confirmation rate < 85% over 24h -> warning
- question no-result rate > 20% over 24h -> warning
- OCR failed rate > 15% over 1h -> warning
- stuck `ocr_processing` count above threshold for 15m -> critical

Thresholds must be tuned with production evidence after launch.

---

## Data Freshness and Retention

- dashboard refresh target: <= 1 minute for operational metrics
- cost and usage aggregates: <= 15 minutes
- raw high-cardinality logs retained per environment policy
- retention must align with GDPR and privacy policy constraints

---

## Incident Integration

- alerts must map to runbook playbooks in `docs/operations-runbook.md`
- every critical alert should include:
- probable cause hints
- first remediation actions
- relevant dashboard deep links

---

## Governance

- updates to thresholds or panel definitions require:
- this document update
- `CHANGELOG.md` update
- validation in staging before production
