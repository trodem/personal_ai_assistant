param(
    [string]$DbService = "postgres",
    [string]$DbUser = "personal_ai",
    [string]$DbName = "personal_ai"
)

$ErrorActionPreference = "Stop"

$sqlPath = Join-Path $PSScriptRoot "sql/local-test-seed.sql"
if (-not (Test-Path -Path $sqlPath)) {
    throw "Seed SQL file not found at $sqlPath"
}

Write-Host "Applying local test seed dataset..."
Get-Content -Path $sqlPath -Raw |
    docker compose exec -T $DbService psql -v ON_ERROR_STOP=1 -U $DbUser -d $DbName
if ($LASTEXITCODE -ne 0) {
    throw "Seed SQL execution failed with exit code $LASTEXITCODE."
}

Write-Host "Seed complete. Current row counts:"
docker compose exec -T $DbService psql -U $DbUser -d $DbName -c @"
select 'users' as table_name, count(*) as row_count from users
union all
select 'memories', count(*) from memories
union all
select 'memory_versions', count(*) from memory_versions
union all
select 'attachments', count(*) from attachments
union all
select 'qa_interactions', count(*) from qa_interactions
union all
select 'memory_audit_log', count(*) from memory_audit_log
order by table_name;
"@
if ($LASTEXITCODE -ne 0) {
    throw "Seed verification query failed with exit code $LASTEXITCODE."
}
