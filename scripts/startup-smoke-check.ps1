$ErrorActionPreference = "Stop"

function Wait-Healthy {
  param(
    [int]$MaxAttempts = 30,
    [int]$SleepSeconds = 3
  )

  for ($i = 0; $i -lt $MaxAttempts; $i++) {
    $raw = docker compose ps --format json
    if (-not $raw) {
      Start-Sleep -Seconds $SleepSeconds
      continue
    }

    $services = $raw | ConvertFrom-Json
    $backend = $services | Where-Object { $_.Service -eq "backend" }
    $postgres = $services | Where-Object { $_.Service -eq "postgres" }

    if ($backend.Health -eq "healthy" -and $postgres.Health -eq "healthy") {
      return
    }

    Start-Sleep -Seconds $SleepSeconds
  }

  throw "Timed out waiting for backend/postgres healthy state."
}

Write-Host "[smoke] validate compose"
docker compose config -q

Write-Host "[smoke] start backend + postgres"
docker compose up -d backend postgres

Write-Host "[smoke] wait for health checks"
Wait-Healthy

if ($env:API_PORT -and $env:API_PORT.Trim()) {
  $apiPort = $env:API_PORT
} else {
  $apiPort = "8000"
}

Write-Host "[smoke] call /health/live"
$live = Invoke-WebRequest "http://localhost:$apiPort/health/live" -UseBasicParsing
if ($live.StatusCode -ne 200) {
  throw "/health/live failed with status $($live.StatusCode)"
}

Write-Host "[smoke] call /health/ready"
$ready = Invoke-WebRequest "http://localhost:$apiPort/health/ready" -UseBasicParsing
if ($ready.StatusCode -ne 200) {
  throw "/health/ready failed with status $($ready.StatusCode)"
}

Write-Host "startup smoke check passed"
