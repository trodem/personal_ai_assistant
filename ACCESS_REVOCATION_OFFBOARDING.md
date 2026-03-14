# Access Revocation Process (Team Offboarding)

## Trigger
- Team member leaves role/project, contract ends, or access must be revoked for security reasons.

## Revocation SLA
- Critical access revocation target: within 4 hours from offboarding trigger.

## Minimum Revocation Checklist
1. Disable/remove repository access (Git hosting organization/repo).
2. Revoke cloud and platform console access (Supabase, OpenAI, Stripe, monitoring, CI).
3. Revoke secret-manager access and rotate shared secrets if exposure risk exists.
4. Invalidate active tokens/sessions where platform supports it.
5. Remove device-specific credentials (CLI tokens, SSH keys, API keys).
6. Update team role matrix and ownership assignments.

## Validation Steps
- Confirm user no longer appears in access lists for each critical system.
- Run a privilege smoke check from a non-privileged account when feasible.
- Record completion timestamp and operator.

## Emergency Path
- If offboarding is security-related, trigger emergency secret rotation and incident flow immediately.

## Audit Trail
- Keep a revocation record with:
  - user identifier
  - systems affected
  - actions completed
  - completion timestamp
  - executor and reviewer
