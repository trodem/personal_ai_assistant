# MVP KPI Baseline

## Locked KPI Targets
- `memory_save_success_rate >= 95%`
- `avg_question_latency_p95 <= 3s` (text query only)
- `voice_pipeline_latency_p95 <= 12s`
- `extraction_confirmation_rate >= 85%`
- `time_to_first_successful_memory <= 2 minutes` (new user onboarding success)

## Measurement Scope
- KPIs are measured on MVP production-like traffic and validated in staging before release decisions.
- Definitions and event derivations must stay aligned with `docs/product-analytics.md`.

## Review Rule
- KPI thresholds are reviewed at each milestone mini-audit and after major flow changes.
