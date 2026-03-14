$ErrorActionPreference = "Stop"

Write-Host "[unit] backend llmops alignment"
python -m unittest backend/tests/test_llmops_alignment.py -v

Write-Host "[integration] backend ai cost metrics + cors preflight"
python -m unittest backend/tests/test_ai_cost_metrics.py backend/tests/test_cors_preflight.py -v

Write-Host "[e2e] backend critical flows"
python -m unittest `
  backend/tests/test_memory_ingestion_e2e.py `
  backend/tests/test_question_engine_db_first.py `
  backend/tests/test_attachment_flow_e2e.py `
  backend/tests/test_security_default.py -v

Write-Host "[mobile] flutter analyze"
Push-Location mobile
try {
  flutter analyze --no-fatal-infos

  Write-Host "[mobile] flutter test"
  flutter test
}
finally {
  Pop-Location
}

Write-Host "test scope checks passed"
