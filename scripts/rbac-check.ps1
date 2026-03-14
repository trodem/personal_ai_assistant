$ErrorActionPreference = "Stop"

$previousPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = "backend"

Write-Host "[rbac] endpoint-role matrix alignment"
python -m unittest backend/tests/test_rbac_matrix_alignment.py -v
$exitCode = $LASTEXITCODE

$env:PYTHONPATH = $previousPythonPath
if ($exitCode -ne 0) {
  exit $exitCode
}

Write-Host "rbac checks passed"
