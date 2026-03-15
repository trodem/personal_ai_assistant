# Coding Standards

## Purpose

Define mandatory implementation standards for Flutter and FastAPI code quality.

These rules are non-negotiable for this project.

---

## Global Standards

- Use English only for identifiers, function/class names, comments, logs, and API documentation.
- Keep code modular, DRY, and easy to maintain.
- Do not ship large unreadable files; split by responsibility.
- Prefer composition and reusable modules over duplicated logic.
- Keep business logic out of UI components.
- Enforce quality gates early with pre-commit hooks when feasible.

---

## Flutter Standards

- Build reusable widgets/components for repeated UI patterns.
- Centralize styling in a single theme system (colors, typography, spacing, tokens).
- Do not hardcode scattered colors/styles across screens.
- Keep screen widgets focused on layout/composition.
- Move state/business logic into dedicated controllers/services/state layers.
- Use placeholder logo for MVP branding with app name: `Personal AI Assistant`.
- Enforce architecture lint rules that prevent business logic inside widgets/screens.

---

## Frontend-Impact Definition of Done

For every task that changes Flutter UI behavior, authentication flow, onboarding flow, or any mobile-to-backend integration path, completion requires all checks below:

- Unit/integration tests for touched logic are green.
- Backend/API smoke check is executed with a real Supabase access token (not only dev-signed local tokens).
- Emulator/manual verification is executed for the exact affected user path (at minimum: login + changed screen/flow outcome).
- A task cannot be marked done if only backend tests pass while frontend flow remains unverified.

---

## FastAPI Standards

- Keep OpenAPI/Swagger docs accurate for every endpoint change.
- Use typed request/response models consistently.
- Keep route handlers thin; move logic to services/repositories.
- Use centralized error handling and stable machine-readable error codes.
- Implement production-grade structured logging:
- correlation IDs (`request_id`, `trace_id`)
- user context when available (`user_id`)
- consistent severity levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- full exception context for failures
- secret/PII redaction in logs
- Validate logging contract with automated log schema tests to keep observability stable.

---

## File Size and Modularity Guidance

- Avoid oversized files that mix multiple responsibilities.
- Refactor when readability drops or responsibilities diverge.
- Organize by feature/domain and explicit interfaces.

---

## Changelog Policy

- Maintain `CHANGELOG.md` for user-visible or developer-relevant changes.
- Update changelog in the same PR/iteration whenever feasible.
- If changelog update is intentionally skipped, document why.
