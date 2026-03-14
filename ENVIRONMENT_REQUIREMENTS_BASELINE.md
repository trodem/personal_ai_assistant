# Environment and Required Variables Baseline

## Environments
- `dev`: local development and smoke checks.
- `staging`: pre-production validation with production-like integrations.
- `prod`: production runtime with strict controls.

## Required Variables (Baseline)

### Core (all environments)
- `APP_ENV`
- `APP_VERSION`
- `API_PORT`
- `LOG_LEVEL`

### Supabase/Auth/DB
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `SUPABASE_DB_URL`
- `SUPABASE_STORAGE_BUCKET_RECEIPTS`

### OpenAI
- `OPENAI_API_KEY`
- `OPENAI_MODEL_TEXT`
- `OPENAI_MODEL_TRANSCRIPTION`
- `AI_TOKEN_BUDGET_FREE`
- `AI_TOKEN_BUDGET_PREMIUM`

### Stripe (billing phases)
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PRICE_PREMIUM_MONTHLY`

### Smoke-test helpers (non-prod)
- `SMOKE_TEST_EMAIL`
- `SMOKE_TEST_PASSWORD`

## Environment-Specific Rules
- `dev` uses local/default-safe values where supported.
- `staging` and `prod` must use environment-specific, isolated credentials.
- No secret values are allowed in source control.

## Source References
- `.env.example`
- `docs/environment-matrix.md`
