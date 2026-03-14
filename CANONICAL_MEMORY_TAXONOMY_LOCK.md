# Canonical Memory Taxonomy and Fields Lock

## Canonical Memory Types
- `expense_event`
- `inventory_event`
- `loan_event`
- `note`
- `document`

## Canonical Semantic Fields
- `who`
- `what`
- `where`
- `when`
- `why`
- `how`

## Contract Rules
- `memory_type` must be one of the canonical values above.
- `structured_data` required fields are defined by memory type (`specs/memory-extraction.md`).
- Semantic fields should be extracted whenever possible and kept in canonical naming.
- `when` defaults to current timestamp when missing, then shown for confirmation/edit before persistence.

## Source References
- `PROJECT_CONTEXT.md`
- `specs/api.yaml` (`MemoryType`, persistence contract)
- `specs/memory-extraction.md` (`required_by_type`, semantic fields)
- `docs/domain-model.md`
