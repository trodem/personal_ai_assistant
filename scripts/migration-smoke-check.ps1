$ErrorActionPreference = "Stop"

function Assert-Condition {
  param(
    [bool]$Condition,
    [string]$Message
  )

  if (-not $Condition) {
    throw $Message
  }
}

Write-Host "[migrations] upgrade to head"
docker compose exec -T backend sh -lc "alembic -c alembic.ini upgrade head"

Write-Host "[migrations] verify probe table exists"
$tableExists = docker compose exec -T postgres psql -U personal_ai -d personal_ai -tAc "select to_regclass('public.alembic_smoke_probe') is not null;"
Assert-Condition -Condition ($tableExists.Trim().ToLower() -eq "t") -Message "Expected alembic_smoke_probe table to exist after upgrade."

Write-Host "[migrations] downgrade to base"
docker compose exec -T backend sh -lc "alembic -c alembic.ini downgrade base"

Write-Host "[migrations] verify probe table removed"
$tableExistsAfterDowngrade = docker compose exec -T postgres psql -U personal_ai -d personal_ai -tAc "select to_regclass('public.alembic_smoke_probe') is not null;"
Assert-Condition -Condition ($tableExistsAfterDowngrade.Trim().ToLower() -eq "f") -Message "Expected alembic_smoke_probe table to be removed after downgrade."

Write-Host "[migrations] restore to head"
docker compose exec -T backend sh -lc "alembic -c alembic.ini upgrade head"

Write-Host "migration smoke checks passed"
