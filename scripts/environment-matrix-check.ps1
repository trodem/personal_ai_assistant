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

Assert-Contains -Content $envContent -Expected "APP_ENV=dev" -Message "Expected APP_ENV=dev in .env.example for dev-default profile."
Assert-Contains -Content $envContent -Expected "SUPABASE_URL=http://127.0.0.1:54321" -Message "Expected local Supabase URL default in .env.example."
Assert-Contains -Content $envContent -Expected "SUPABASE_DB_URL=postgresql://personal_ai:personal_ai@localhost:5432/personal_ai" -Message "Expected local Postgres URL in .env.example."

Assert-Contains -Content $composeContent -Expected "APP_ENV: ${APP_ENV:-dev}" -Message "Expected docker-compose backend APP_ENV default to dev."
Assert-Contains -Content $composeContent -Expected "SUPABASE_URL: ${SUPABASE_URL:-}" -Message "Expected docker-compose backend SUPABASE_URL wiring."
Assert-Contains -Content $composeContent -Expected "SUPABASE_JWT_SECRET: ${SUPABASE_JWT_SECRET:-}" -Message "Expected docker-compose backend SUPABASE_JWT_SECRET wiring."

Write-Host "environment matrix checks passed"
