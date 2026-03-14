# Billing Alert Thresholds (MVP)

## Alert Policy
Billing-related AI spend alerts must expose at least `warning` and `critical` severities.

## Defined Thresholds
- Daily spend vs 7-day moving average:
  - `warning`: > 120%
  - `critical`: > 160%
- Monthly budget burn projection:
  - `warning`: > 110%
  - `critical`: > 130%

## Runtime Source of Truth
- Implemented in `backend/app/core/llmops.py` as alert thresholds.
- Exposed via metrics (`llmops_alert_threshold`, `llmops_spend_spike_alert_active`).

## Verification
- Run:
  - `python -m unittest backend.tests.test_llmops_alignment backend.tests.test_ai_cost_metrics`
- Expected:
  - tests pass
  - warning/critical thresholds for spend and budget are present.
