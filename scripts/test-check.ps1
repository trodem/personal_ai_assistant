$ErrorActionPreference = "Stop"

Write-Host "running backend unit and integration tests"
python -m unittest discover -s backend/tests -p "test_*.py" -v

Write-Host "test checks passed"
