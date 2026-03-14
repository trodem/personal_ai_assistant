# Privacy Policy Baseline (MVP)

## Scope
This baseline applies to the Personal AI Assistant MVP and defines the minimum privacy commitments for data collection, storage, retention, and deletion.

## Data We Store
- Account and authentication data (email, role, account status, MFA status where applicable).
- User-provided memory content (voice transcripts, text memories, structured extracted fields).
- Attachment metadata and receipt-photo files.
- Operational telemetry (request IDs, trace IDs, error events, AI usage/cost metrics).

## Purpose of Processing
- Provide core product functionality (memory capture, retrieval, question answering).
- Ensure security, reliability, and abuse prevention.
- Support billing and plan policy enforcement where applicable.

## Storage and Security Baseline
- Data is stored in Supabase services (Auth, Postgres, Storage) and related runtime infrastructure.
- Access is restricted by authenticated identity and user/tenant isolation rules.
- Secrets must not be stored in source control.
- Public file access is disabled for receipt storage; access is via short-lived signed URLs.

## Retention Baseline
- Account and memory data are retained while the account is active.
- Orphan uploads (attachments never confirmed into a memory flow) are subject to cleanup policy.
- Operational logs and analytics are retained only for operational and compliance needs, with minimization/redaction rules.

## User Rights Baseline
- Users can request data export (asynchronous flow).
- Users can request account/data deletion according to lifecycle policy.
- Deletion must cover primary DB records, storage objects, embeddings, and relevant caches.

## Deletion Process Baseline
1. User requests deletion or account closure.
2. Account state transitions to deletion workflow state.
3. Background jobs remove user-scoped data from DB, storage, embeddings, and caches.
4. Process is idempotent, audited, and retried on transient failures.
5. Completion status is recorded for operational audit.

## Third-Party Processing Baseline
- AI processing is performed through configured provider integrations for MVP flows.
- Input/output safety and data sanitization policies apply before provider calls.

## Contact Baseline
- A support and privacy contact must be defined before public launch.

## Revision Policy
- This baseline is a pre-launch draft and must be reviewed with legal/compliance before production rollout.
