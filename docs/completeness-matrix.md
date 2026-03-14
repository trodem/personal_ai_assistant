# Planning Completeness Matrix

## Purpose

Provide a single operational view of which core product capabilities are covered in planning artifacts.

Status meanings:

- `covered`: explicitly planned with policy + implementation tasks
- `partial`: partially planned; one or more contracts/policies missing
- `missing`: not planned

---

## Matrix

| Capability | Status | Primary Planning Docs | API/Contract Coverage | TODO Coverage |
|---|---|---|---|---|
| Subscription management (`free`/`premium`) | covered | `docs/monetization.md`, `docs/development-roadmap.md` | `specs/api.yaml` billing endpoints | `P10` |
| Payment methods in user settings | covered | `docs/monetization.md`, `docs/system-architecture.md` | payment-method endpoints in `specs/api.yaml` | `P4`, `P7`, `P10` |
| Auth (email/password + SSO + 2FA) | covered | `docs/decisions.md`, `docs/system-architecture.md` | settings/security + auth-related contracts | `P5`, quality gates |
| Notification channels (in-app/push/email) | covered | `docs/decisions.md`, `docs/system-architecture.md` | notification endpoints + preferences | `P4`, `P7`, `P10.5` |
| Localization (`en`/`it`/`de`) | covered | `docs/system-architecture.md`, `docs/query-contract.md` | `preferred_language` in settings schemas | `P0`, `P7`, quality gates |
| Guided onboarding | covered | `docs/system-architecture.md`, `docs/product-analytics.md` | UX contract in `docs/ai-ux-contract.md` | `P7` |
| AI UX contract (clarification/confirm/why-this-answer) | covered | `docs/ai-ux-contract.md` | query + memory contracts | quality gates, `P7` |
| LLMOps observability | covered | `docs/llmops-dashboard-spec.md`, `docs/operations-runbook.md` | error + metric conventions in docs | quality gates, `P11`, `P13` |
| Prompt/model governance | covered | `docs/model-registry.md` | prompt spec + model registry policy | `P3`, `P11`, quality gates |
| Rate limiting and usage quotas | covered | `docs/ai-cost-control.md`, `docs/monetization.md` | policy-level; endpoint-level enforcement tasks | `P10`, `P11` |
| Streaming responses (SSE) | covered | `docs/query-contract.md`, `docs/ai-ux-contract.md` | `/api/v1/question/stream` | `P4`, `P6`, `P7` |
| Semantic caching | covered | `docs/semantic-caching.md`, `docs/query-contract.md` | policy-level behavior contract | `P6`, `P11` |
| Fallback and provider redundancy | covered | `docs/model-registry.md`, `docs/operations-runbook.md` | error/fallback policies | `P11`, `P13` |
| Content moderation | covered | `docs/content-moderation.md` | error codes + moderation actions | `P3`, `P6`, `P12` |
| Data sanitization/anonymization pre-LLM | covered | `docs/data-sanitization.md` | error/event mapping + policy | `P3`, `P12` |
| Data isolation (user-level) | covered | `docs/security-threat-model.md`, `docs/rbac-matrix.md` | RBAC + isolation contracts | quality gates, `P2`, `P5` |
| Multi-tenancy B2B isolation path | covered | `docs/multi-tenancy.md` | tenant policy contract | `P2`, `P5` (tenant-ready tasks) |
| Audit logs and traceability | covered | `docs/security-threat-model.md`, `docs/operations-runbook.md` | error/logging conventions | quality gates, `P1`, `P12` |
| Data lifecycle and right-to-be-forgotten | covered | `docs/data-lifecycle.md` | lifecycle policy contract | `P12`, `P13` |
| Data portability export (`json`/`csv`/`pdf`) | covered | `docs/data-portability.md` | export job endpoints in `specs/api.yaml` | `P4`, `P12` |
| Churn management (predictive + cancel retention) | covered | `docs/churn-management.md`, `docs/monetization.md` | retention/cancel endpoints in `specs/api.yaml` | `P10` |
| Trial/coupon/discount management | covered | `docs/trial-and-freemium.md`, `docs/monetization.md` | trial/coupon endpoints in `specs/api.yaml` | `P10` |
| Feature flags and A/B testing | covered | `docs/feature-flags-experiments.md` | policy-level governance | `P11`, `P13` |
| API backward compatibility lifecycle | covered | `docs/api-compatibility.md`, `docs/decisions.md` | versioning + deprecation policy | quality gates, `P4`, `P13` |

---

## Governance

- update this matrix whenever a capability status changes
- changes must be synchronized with `TODO.md` and `CHANGELOG.md`
