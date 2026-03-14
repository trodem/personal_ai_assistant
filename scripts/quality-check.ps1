$ErrorActionPreference = "Stop"

Write-Host "[lint] docker compose config"
docker compose config -q

Write-Host "[lint] python compileall backend/tests"
python -m compileall backend/tests

Write-Host "[test] python unittest"
python -m unittest discover -s backend/tests -p "test_*.py" -v

Write-Host "[build] docker compose build"
docker compose build

Write-Host "quality checks passed"
