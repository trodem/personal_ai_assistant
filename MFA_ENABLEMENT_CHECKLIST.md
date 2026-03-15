# MFA Enablement Checklist (Day 0 Blocker Resolution)

Purpose: complete the TODO task `Enable MFA everywhere and store recovery codes securely`.

Status: `blocked` until all provider-side manual steps below are completed.

## Services in scope
- Git hosting account
- OpenAI account
- Supabase account
- Stripe account

## Required outcome per service
- MFA is enabled.
- Recovery codes are generated.
- Recovery codes are stored in a secure vault (not in repository, not in `.env`, not in chat logs).
- Last verification date is recorded.

## Evidence log
Fill one row per service after completing the provider console steps.

| Service | MFA Enabled (`yes/no`) | Recovery Codes Generated (`yes/no`) | Secure Storage Location (label only) | Verified By | Verified On (YYYY-MM-DD) |
|---|---|---|---|---|---|
| Git hosting | no | no | TODO | TODO | TODO |
| OpenAI | no | no | TODO | TODO | TODO |
| Supabase | no | no | TODO | TODO | TODO |
| Stripe | no | no | TODO | TODO | TODO |

## Completion rule
When all rows are `yes` for MFA and recovery codes:
1. Mark TODO task `Enable MFA everywhere and store recovery codes securely.` as completed.
2. Keep this checklist updated for future periodic re-verification.
