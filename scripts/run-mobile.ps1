param(
  [string]$DeviceId = "RFCR80K8WQV",
  [string]$ApiBaseUrl = "http://10.0.2.2:8000",
  [string]$EnvFile = ".env",
  [switch]$PrintOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $EnvFile)) {
  throw "Env file not found: $EnvFile"
}

$lines = Get-Content $EnvFile

function Get-EnvValue([string]$key) {
  $line = $lines | Where-Object { $_ -match ("^" + [regex]::Escape($key) + "=") } | Select-Object -First 1
  if ($null -eq $line) {
    throw "Missing key in env file: $key"
  }
  return $line.Substring($key.Length + 1).Trim()
}

$supabaseUrl = Get-EnvValue "SUPABASE_URL"
$supabaseAnonKey = Get-EnvValue "SUPABASE_ANON_KEY"

if ([string]::IsNullOrWhiteSpace($supabaseUrl) -or $supabaseUrl -eq "replace_me") {
  throw "SUPABASE_URL is empty/placeholder in $EnvFile"
}

if ([string]::IsNullOrWhiteSpace($supabaseAnonKey) -or $supabaseAnonKey -eq "replace_me") {
  throw "SUPABASE_ANON_KEY is empty/placeholder in $EnvFile"
}

$runArgs = @(
  "run",
  "-d", $DeviceId,
  "--dart-define=SUPABASE_URL=$supabaseUrl",
  "--dart-define=SUPABASE_ANON_KEY=$supabaseAnonKey",
  "--dart-define=API_BASE_URL=$ApiBaseUrl"
)

Write-Host "Starting Flutter with root env values..." -ForegroundColor Green
$safePreview = @(
  "run",
  "-d", $DeviceId,
  "--dart-define=SUPABASE_URL=$supabaseUrl",
  "--dart-define=SUPABASE_ANON_KEY=***REDACTED***",
  "--dart-define=API_BASE_URL=$ApiBaseUrl"
)
Write-Host ("flutter " + ($safePreview -join " ")) -ForegroundColor DarkGray

if ($PrintOnly) {
  return
}

Push-Location "mobile"
try {
  flutter @runArgs
}
finally {
  Pop-Location
}
