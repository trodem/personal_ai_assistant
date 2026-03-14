# MVP Language Matrix Lock

## Locked Language Matrix
- Supported languages: `en`, `it`, `de`
- Default fallback language: `en`

## Policy Rules
- `preferred_language` must accept only `en`, `it`, `de`.
- If a preferred-language response is not available, fallback must be English (`en`).
- Do not mix partial fallback fragments across languages in a single response.

## Reference Alignment
- `PROJECT_CONTEXT.md` (`preferred_language` + fallback contract)
- `docs/system-architecture.md` (language matrix and fallback behavior)
- `specs/api.yaml` (`preferred_language` enum: `en`, `it`, `de`)
