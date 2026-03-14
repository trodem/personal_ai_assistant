$ErrorActionPreference = "Stop"

Write-Host "[ai-safety] moderation + sanitization policy alignment"
$previousPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = "backend"
python -m unittest backend/tests/test_ai_safety_alignment.py -v
$exitCode = $LASTEXITCODE
$env:PYTHONPATH = $previousPythonPath
if ($exitCode -ne 0) {
  exit $exitCode
}

Write-Host "ai safety checks passed"
