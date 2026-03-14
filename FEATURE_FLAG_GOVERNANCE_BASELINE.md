# Feature-Flag Governance Baseline (MVP)

## Naming Convention
- Pattern: `ff_<domain>_<capability>_<variant>`
- Use lowercase snake_case only.
- Example: `ff_ai_answer_streaming_v1`

## Ownership
- Each flag must define:
  - business owner (product decision authority)
  - technical owner (implementation and rollback authority)
- Ownership must be documented before enabling a flag in non-dev environments.

## Expiry Policy
- Every flag must include:
  - creation date
  - target removal date
  - review cadence
- Default max lifetime for temporary flags: 90 days.

## Kill-Switch Requirement
- Every high-risk flag must support immediate disable without redeploy.
- Kill-switch path must be documented and tested in staging before production use.

## Minimum Metadata
- `name`
- `description`
- `owner_business`
- `owner_technical`
- `created_at`
- `expires_at`
- `default_state` (`on`/`off`)
- `kill_switch` (`true`/`false`)

## Reference Alignment
- `docs/feature-flags-experiments.md`
- `TODO.md` P0 governance checklist
