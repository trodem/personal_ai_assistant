$ErrorActionPreference = "Stop"

$ruff = Get-Command ruff -ErrorAction SilentlyContinue
if (-not $ruff) {
  Write-Host "ruff not found, installing..."
  python -m pip install ruff==0.6.8 | Out-Null
}

Write-Host "running ruff lint checks (F,E9) on backend/"
ruff check backend --select F,E9

Write-Host "lint checks passed"
