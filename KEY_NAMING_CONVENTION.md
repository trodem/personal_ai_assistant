# Key Naming Convention (MVP)

## Canonical Pattern
Use the following pattern for credentials and secrets:

`APP_<SERVICE>_<ENV>_<PURPOSE>`

## Rules
- Uppercase only.
- Use `_` as separator.
- `<ENV>` must be one of: `DEV`, `STAGING`, `PROD`.
- `<SERVICE>` should be concise and stable (for example: `OPENAI`, `SUPABASE`, `STRIPE`).
- `<PURPOSE>` describes intended usage (`API_KEY`, `WEBHOOK_SECRET`, `JWT_SECRET`, etc.).

## Examples
- `APP_OPENAI_DEV_API_KEY`
- `APP_OPENAI_PROD_API_KEY`
- `APP_SUPABASE_STAGING_SERVICE_ROLE_KEY`
- `APP_SUPABASE_PROD_JWT_SECRET`
- `APP_STRIPE_DEV_WEBHOOK_SECRET`
- `APP_STRIPE_PROD_SECRET_KEY`

## Notes
- Keep naming consistent across secret manager and deployment variables.
- Do not store real secret values in source control.
