$ErrorActionPreference = "Stop"

Write-Host "[security] auth + tenant isolation"
python -m unittest backend/tests/test_security_default.py -v

Write-Host "[security] privileged access + mfa policy"
python -m unittest backend/tests/test_mfa_policy.py -v

Write-Host "[security] attachment upload and signed-url authorization"
python -m unittest backend/tests/test_attachment_flow_e2e.py -v

Write-Host "[security] structured log redaction"
python -m unittest backend/tests/test_logging_redaction.py -v

Write-Host "security threat-model checks passed"
