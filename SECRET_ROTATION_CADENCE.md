# Secret Rotation Cadence (MVP)

## Baseline Cadence
- Standard rotation interval: every 90 days.

## Scope
- API keys (OpenAI, Stripe, other external providers).
- Supabase service-role and JWT-related secrets.
- Webhook signing secrets.
- Any environment credential used in `staging` or `prod`.

## Rotation Procedure (Minimum)
1. Generate new secret/key in provider console.
2. Store new value in secret manager/deployment environment.
3. Roll out new secret to runtime.
4. Validate critical smoke checks.
5. Revoke old secret after validation window.
6. Record rotation date, owner, and evidence.

## Emergency Rotation
- Trigger immediate rotation after suspected leak, unauthorized access, or provider security incident.
- Incident owner coordinates emergency rotation and post-rotation validation.

## Ownership
- Primary owner: incident owner / platform owner.
- Backup owner: designated backup in support/incident ownership baseline.
