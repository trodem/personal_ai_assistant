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

$loginBody = @{ email = $email; password = $password } | ConvertTo-Json -Compress
$loginHeaders = @{
  "apikey" = $anonKey
  "Content-Type" = "application/json"
}

Write-Host "[supabase] login for token"
$login = Invoke-RestMethod -Method POST -Uri "$supabaseUrl/auth/v1/token?grant_type=password" -Headers $loginHeaders -Body $loginBody
if (-not $login.access_token) {
  throw "Supabase login succeeded but no access_token in response."
}

Write-Host "[backend] protected call with Supabase token"
$backendHeaders = @{
  "Authorization" = "Bearer $($login.access_token)"
}
$response = Invoke-RestMethod -Method GET -Uri "http://localhost:8000/api/v1/memories" -Headers $backendHeaders

if ($null -eq $response.items) {
  throw "Protected API call did not return expected payload."
}

Write-Host "supabase auth smoke passed"
