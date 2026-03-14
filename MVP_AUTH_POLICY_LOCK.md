# MVP Authentication Policy Lock

## Locked Authentication Baseline
- Provider: Supabase Auth
- Login methods:
  - Email/Password
  - OAuth SSO: Google, Apple

## 2FA Policy
- 2FA available for all users.
- 2FA mandatory for privileged roles: `admin`, `author`.
- Privileged actions must be blocked when required 2FA is missing.

## Reference Alignment
- `PROJECT_CONTEXT.md` (auth methods + 2FA policy)
- `docs/system-architecture.md` (auth + role-based 2FA behavior)
- `docs/decisions.md` (MVP auth policy decisions)
- `specs/api.yaml` (`/api/v1/me/settings/security`, `mfa_enabled`)
