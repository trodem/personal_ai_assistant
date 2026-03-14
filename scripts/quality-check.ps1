$ErrorActionPreference = "Stop"

function Wait-Healthy {
  param(
    [int]$MaxAttempts = 24,
    [int]$SleepSeconds = 5
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

  throw "Timed out waiting for backend/postgres to become healthy."
}

Write-Host "[lint] docker compose config"
docker compose config -q

Write-Host "[runtime] docker compose up -d"
docker compose up -d

Write-Host "[runtime] wait for healthy services"
Wait-Healthy

Write-Host "[lint] python compileall backend/tests"
python -m compileall backend/tests

Write-Host "[test] python unittest (unit + integration)"
python -m unittest discover -s backend/tests -p "test_*.py" -v

Write-Host "[build] docker compose build"
docker compose build

Write-Host "quality checks passed"
