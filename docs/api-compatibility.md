# API Backward Compatibility Policy

## Purpose

Define how API changes are introduced without breaking older app versions.

---

## Scope

Applies to all `/api/v*` endpoints and mobile clients that may lag behind latest release.

---

## Compatibility Rules

- additive changes are preferred (new optional fields/endpoints)
- breaking changes require:
- new API version path (for example `/api/v2/...`)
- migration plan
- deprecation timeline

- existing required fields must not be removed in active API version
- response fields used by released clients must remain stable during support window

---

## Deprecation and Sunset

- minimum deprecation window for mobile-impacting changes: 90 days
- deprecated endpoints must return deprecation metadata (header and docs notice)
- sunset date must be explicit and communicated

Recommended headers:

- `Deprecation: true`
- `Sunset: <http-date>`
- `Link: <deprecation-doc-url>; rel="deprecation"`

---

## Client Support Matrix

Maintain and publish supported client versions:

- latest stable
- previous minor version (minimum)

Requests from unsupported versions should receive clear upgrade guidance.

---

## Change Process

Before introducing potentially breaking API behavior:

1. update `specs/api.yaml`
2. update this compatibility policy if needed
3. add compatibility tests (current + previous client contract)
4. update `CHANGELOG.md`

---

## Governance

- this policy is mandatory for release planning
- exceptions require explicit approval and incident-risk acknowledgment
