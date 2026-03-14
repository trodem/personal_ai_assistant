# RBAC Matrix

## Purpose

Define a single source of truth for role permissions at endpoint level.

Roles:

- `user` (product alias: `subscriber`)
- `admin`
- `author` (highest privilege)

Role hierarchy:

`author > admin > user`

---

## Global Policy

- `author` inherits all `admin` permissions.
- `admin` and `author` are always `premium` and `billing_exempt=true`.
- `author` is the only role allowed to change roles (`user` <-> `admin`).
- `admin` and `author` must keep 2FA enabled.
- `author` safety invariants:
- `author` cannot change own role.
- `author` cannot suspend/cancel own account.
- operations that would remove the last active author are forbidden.

---

## Endpoint Permission Matrix

| Endpoint | user | admin | author | Notes |
|---|---|---|---|---|
| `POST /api/v1/voice/memory` | allow | allow | allow | blocked if status is `suspended`/`canceled` |
| `POST /api/v1/voice/question` | allow | allow | allow | blocked if status is `suspended`/`canceled` |
| `POST /api/v1/question` | allow | allow | allow | blocked if status is `suspended`/`canceled` |
| `POST /api/v1/memory` | allow | allow | allow | explicit confirm required |
| `GET /api/v1/memories` | allow | allow | allow | user-scoped data only |
| `DELETE /api/v1/memory/{id}` | allow | allow | allow | user-scoped ownership checks |
| `POST /api/v1/attachments` | allow | allow | allow | receipt photos only |
| `GET /api/v1/dashboard` | allow | allow | allow | personal dashboard |
| `GET /api/v1/me/settings` | allow | allow | allow | own settings only |
| `PATCH /api/v1/me/settings/profile` | allow | allow | allow | own settings only |
| `PATCH /api/v1/me/settings/security` | allow | allow | allow | own settings only + notification + 2FA challenge for sensitive changes |
| `POST /api/v1/billing/subscription/change-plan` | allow | deny | deny | `admin`/`author` plan locked by role policy |
| `GET /api/v1/admin/users` | deny | allow | allow | admin surface |
| `PATCH /api/v1/admin/users/{id}/status` | deny | allow | allow | status: `active`/`suspended`/`canceled` |
| `GET /api/v1/author/dashboard` | deny | deny | allow | global supervision dashboard |
| `PATCH /api/v1/author/users/{id}/role` | deny | deny | allow | `user` <-> `admin` only |

---

## Required Enforcement Tests

- `user` denied on admin/author endpoints (`403`)
- `admin` denied on author-only endpoints (`403`)
- `author` role transition constraints enforced (self-change forbidden, last-author protection)
- `admin`/`author` denied on self-service subscription change endpoint (`403 billing.plan_locked_by_role`)
- `admin`/`author` denied on privileged actions when 2FA is not enabled (`403 auth.mfa_required`)
- suspended/canceled account denied on protected endpoints

---

## Change Management

- Any role/endpoint change must update this file, `specs/api.yaml`, and `TODO.md` in the same iteration.
