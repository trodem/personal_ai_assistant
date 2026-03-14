$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
  throw "Missing .env file. Create it from .env.example and set Supabase credentials."
}

Get-Content ".env" | ForEach-Object {
  if ($_ -match "^\s*#") { return }
  if ($_ -match "^\s*$") { return }
  $parts = $_ -split "=", 2
  if ($parts.Length -eq 2) {
    [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], "Process")
  }
}

$required = @("SUPABASE_URL", "SUPABASE_ANON_KEY", "SMOKE_TEST_EMAIL", "SMOKE_TEST_PASSWORD")
foreach ($var in $required) {
  if (-not [System.Environment]::GetEnvironmentVariable($var, "Process")) {
    throw "Missing required env var: $var"
  }
}

$supabaseUrl = [System.Environment]::GetEnvironmentVariable("SUPABASE_URL", "Process").TrimEnd("/")
$anonKey = [System.Environment]::GetEnvironmentVariable("SUPABASE_ANON_KEY", "Process")
$email = [System.Environment]::GetEnvironmentVariable("SMOKE_TEST_EMAIL", "Process")
$password = [System.Environment]::GetEnvironmentVariable("SMOKE_TEST_PASSWORD", "Process")

# Docker compose may require "$$" escaping in .env; Supabase Auth needs the literal password.
$normalizedPassword = $password -replace "\$\$", "$"

$loginBody = @{ email = $email; password = $normalizedPassword } | ConvertTo-Json -Compress
$loginHeaders = @{
  "apikey" = $anonKey
  "Content-Type" = "application/json"
}

Write-Host "[supabase/auth] email-password login"
$login = Invoke-RestMethod -Method POST -Uri "$supabaseUrl/auth/v1/token?grant_type=password" -Headers $loginHeaders -Body $loginBody
if (-not $login.access_token) {
  throw "Supabase Auth login succeeded but no access_token in response."
}

$accessHeaders = @{
  "apikey" = $anonKey
  "Authorization" = "Bearer $($login.access_token)"
}

Write-Host "[supabase/postgrest] db API reachability"
$restResponse = Invoke-WebRequest -Method GET -Uri "$supabaseUrl/rest/v1/" -Headers $accessHeaders
if ($restResponse.StatusCode -lt 200 -or $restResponse.StatusCode -ge 300) {
  throw "Supabase PostgREST endpoint is not reachable."
}

Write-Host "[supabase/storage] bucket API reachability"
$storageResponse = Invoke-WebRequest -Method GET -Uri "$supabaseUrl/storage/v1/bucket" -Headers $accessHeaders
if ($storageResponse.StatusCode -lt 200 -or $storageResponse.StatusCode -ge 300) {
  throw "Supabase Storage endpoint is not reachable."
}

Write-Host "supabase project reachability checks passed"
