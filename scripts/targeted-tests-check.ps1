$ErrorActionPreference = "Stop"

Write-Host "running targeted fast tests for local pre-commit"
python -m unittest `
  backend/tests/test_openapi_docs.py `
  backend/tests/test_error_model_contract.py `
  backend/tests/test_security_default.py -v

Write-Host "targeted tests passed"
