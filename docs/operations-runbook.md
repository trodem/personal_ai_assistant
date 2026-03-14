# Operations Runbook

## Purpose

Define incident response playbooks for high-impact failures.

This document complements:

- `docs/risk-analysis.md` (risk identification)
- `docs/environment-matrix.md` (where systems run)
- `docs/llmops-dashboard-spec.md` (AI monitoring panels and alert thresholds)

---

## Incident Roles

- Incident Commander: coordinates triage and decisions
- Operator: executes technical remediation
- Communicator: updates stakeholders/users

At least one backup must be defined for each role.

---

## Severity Levels

- `SEV-1`: core product unavailable, security breach, data risk
- `SEV-2`: major feature degraded (voice, query, auth)
- `SEV-3`: partial degradation with workaround

---

## Global Incident Flow

1. Detect and classify severity
2. Stabilize impact (containment)
3. Identify root cause
4. Apply fix or rollback
5. Verify recovery with smoke checks
6. Publish post-incident notes and follow-up actions

---

## Playbook: OpenAI/LLM Outage

Symptoms:

- high 5xx from AI-dependent endpoints
- increased latency/timeouts

Actions:

1. switch to degraded mode (no advanced AI responses where possible)
2. enforce strict retries/timeouts
3. surface temporary degraded-message to user
4. monitor provider status and internal error rates

Exit criteria:

- success rate and latency return within defined SLO

---

## Playbook: Database Outage

Symptoms:

- readiness failure
- query errors/timeouts

Actions:

1. stop write-heavy operations if data integrity is at risk
2. verify DB connectivity, credentials, and infra status
3. failover/restore according to environment policy
4. run migration/state consistency checks after recovery

Exit criteria:

- DB readiness green
- critical read/write smoke tests pass

---

## Playbook: Object Storage Outage

Symptoms:

- attachment upload/download failures

Actions:

1. isolate attachment endpoints into degraded mode
2. preserve memory creation without attachment loss where possible
3. retry with backoff for temporary errors
4. recover and reprocess queued operations if implemented

Exit criteria:

- upload and signed URL access tests pass

---

## Playbook: OCR/Attachment Pipeline Degradation

Symptoms:

- attachments stuck in `ocr_processing`
- spike in `ocr.processing_failed` or low-confidence OCR outcomes
- orphan attachment growth

Actions:

1. pause new OCR jobs only if queue overload threatens core API stability
2. keep uploads accepted when possible and mark deterministic status
3. retry OCR jobs with bounded backoff and dead-letter failed jobs
4. run orphan cleanup policy and verify DB/storage consistency
5. communicate clear user action (`Retry`, `Modify manually`, `Cancel`)

Exit criteria:

- attachment lifecycle backlog returns to baseline
- `ocr_processing` stuck count below alert threshold
- no orphan growth trend beyond retention target

---

## Playbook: Auth Provider Issues

Symptoms:

- token validation failures spike
- login flow unavailable

Actions:

1. verify provider status and key configuration
2. confirm JWT validation config and clock skew
3. keep protected endpoints secure (never bypass auth)
4. communicate impact and expected recovery

Exit criteria:

- protected endpoint auth checks (`401`/`200`) restored

---

## Post-Incident Requirements

- timeline of events
- root cause
- impact analysis
- corrective actions with owners and deadlines
