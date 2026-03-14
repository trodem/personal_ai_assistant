$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
  throw "Missing .env file. Create it from .env.example and set OpenAI credentials."
}

Get-Content ".env" | ForEach-Object {
  if ($_ -match "^\s*#") { return }
  if ($_ -match "^\s*$") { return }
  $parts = $_ -split "=", 2
  if ($parts.Length -eq 2) {
    [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], "Process")
  }
}

$apiKey = [System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "Process")
if (-not $apiKey) {
  throw "Missing required env var: OPENAI_API_KEY"
}

$model = [System.Environment]::GetEnvironmentVariable("OPENAI_MODEL_TEXT", "Process")
if (-not $model) {
  $model = "gpt-4.1-mini"
}

$headers = @{
  "Authorization" = "Bearer $apiKey"
  "Content-Type" = "application/json"
}

Write-Host "[openai] key validation via models API"
$null = Invoke-RestMethod -Method GET -Uri "https://api.openai.com/v1/models?limit=1" -Headers $headers -TimeoutSec 30

Write-Host "[openai] billing availability via minimal completion"
$body = @{
  model = $model
  messages = @(@{ role = "user"; content = "Say ok" })
  max_completion_tokens = 5
} | ConvertTo-Json -Compress

$response = Invoke-RestMethod -Method POST -Uri "https://api.openai.com/v1/chat/completions" -Headers $headers -Body $body -TimeoutSec 30
if (-not $response.choices) {
  throw "OpenAI completion call returned no choices."
}

Write-Host "openai account checks passed"
