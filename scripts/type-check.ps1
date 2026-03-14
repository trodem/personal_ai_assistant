$ErrorActionPreference = "Stop"

$mypy = Get-Command mypy -ErrorAction SilentlyContinue
if (-not $mypy) {
  Write-Host "mypy not found, installing..."
  python -m pip install mypy==1.11.2 | Out-Null
}

Write-Host "running baseline type checks"
mypy backend/app/api/schemas.py --ignore-missing-imports

Write-Host "type checks passed"
