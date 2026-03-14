$ErrorActionPreference = "Stop"

$envExamplePath = ".env.example"
$composePath = "docker-compose.yml"

if (-not (Test-Path $envExamplePath)) {
  throw "Missing $envExamplePath"
}
if (-not (Test-Path $composePath)) {
  throw "Missing $composePath"
}

$envContent = Get-Content $envExamplePath -Raw
$composeContent = Get-Content $composePath -Raw

function Assert-Contains {
  param(
    [string]$Content,
    [string]$Expected,
    [string]$Message
  )

  if (-not $Content.Contains($Expected)) {
    throw $Message
  }
}

Assert-Contains -Content $envContent -Expected "APP_ENV=dev" -Message "Missing APP_ENV in .env.example."
Assert-Contains -Content $envContent -Expected "APP_VERSION=dev" -Message "Missing APP_VERSION in .env.example."
Assert-Contains -Content $envContent -Expected "LOG_LEVEL=INFO" -Message "Missing LOG_LEVEL in .env.example."
Assert-Contains -Content $envContent -Expected "SUPABASE_URL=" -Message "Missing SUPABASE_URL in .env.example."
Assert-Contains -Content $envContent -Expected "SUPABASE_JWT_SECRET=" -Message "Missing SUPABASE_JWT_SECRET in .env.example."
Assert-Contains -Content $envContent -Expected "APP_DEV_JWT_SECRET=dev_jwt_secret" -Message "Missing APP_DEV_JWT_SECRET in .env.example."
Assert-Contains -Content $envContent -Expected "OPENAI_API_KEY=" -Message "Missing OPENAI_API_KEY in .env.example."
Assert-Contains -Content $envContent -Expected "OPENAI_MODEL_TEXT=" -Message "Missing OPENAI_MODEL_TEXT in .env.example."
Assert-Contains -Content $envContent -Expected "APP_CORS_ALLOW_ORIGINS=" -Message "Missing APP_CORS_ALLOW_ORIGINS in .env.example."
Assert-Contains -Content $envContent -Expected "AI_TOKEN_BUDGET_FREE=" -Message "Missing AI_TOKEN_BUDGET_FREE in .env.example."
Assert-Contains -Content $envContent -Expected "AI_TOKEN_BUDGET_PREMIUM=" -Message "Missing AI_TOKEN_BUDGET_PREMIUM in .env.example."

Assert-Contains -Content $composeContent -Expected "APP_ENV: ${APP_ENV:-dev}" -Message "docker-compose must map APP_ENV for backend."
Assert-Contains -Content $composeContent -Expected "APP_VERSION: ${APP_VERSION:-dev}" -Message "docker-compose must map APP_VERSION for backend."
Assert-Contains -Content $composeContent -Expected "APP_CORS_ALLOW_ORIGINS:" -Message "docker-compose must map APP_CORS_ALLOW_ORIGINS for backend."
Assert-Contains -Content $composeContent -Expected "AI_TOKEN_BUDGET_FREE:" -Message "docker-compose must map AI_TOKEN_BUDGET_FREE for backend."
Assert-Contains -Content $composeContent -Expected "AI_TOKEN_BUDGET_PREMIUM:" -Message "docker-compose must map AI_TOKEN_BUDGET_PREMIUM for backend."
Assert-Contains -Content $composeContent -Expected "SUPABASE_URL: ${SUPABASE_URL:-}" -Message "docker-compose must map SUPABASE_URL for backend."
Assert-Contains -Content $composeContent -Expected "SUPABASE_JWT_SECRET: ${SUPABASE_JWT_SECRET:-}" -Message "docker-compose must map SUPABASE_JWT_SECRET for backend."

Write-Host "env example completeness checks passed"
