$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
  throw "Missing .env file. Create it from .env.example and set Supabase credentials."
}

Get-Content ".env" | ForEach-Object {
  if ($_ -match "^\s*#") { return }
  if ($_ -match "^\s*$") { return }
  $parts = $_ -split "=", 2
  if ($parts.Length -eq 2) {
    [System.Environment]::SetEnvironmentVariable($parts[0], $parts[1], "Process")
  }
}

$required = @("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_STORAGE_BUCKET_RECEIPTS")
foreach ($var in $required) {
  $value = [System.Environment]::GetEnvironmentVariable($var, "Process")
  if (-not $value -or $value -eq "replace_me") {
    throw "Missing required env var: $var"
  }
}

$supabaseUrl = [System.Environment]::GetEnvironmentVariable("SUPABASE_URL", "Process").TrimEnd("/")
$serviceRoleKey = [System.Environment]::GetEnvironmentVariable("SUPABASE_SERVICE_ROLE_KEY", "Process")
$bucket = [System.Environment]::GetEnvironmentVariable("SUPABASE_STORAGE_BUCKET_RECEIPTS", "Process")
$objectPath = "smoke-tests/storage-upload-download.txt"

$uploadHeaders = @{
  "apikey" = $serviceRoleKey
  "Authorization" = "Bearer $serviceRoleKey"
  "x-upsert" = "true"
}

$downloadHeaders = @{
  "apikey" = $serviceRoleKey
  "Authorization" = "Bearer $serviceRoleKey"
}

$deleteHeaders = @{
  "apikey" = $serviceRoleKey
  "Authorization" = "Bearer $serviceRoleKey"
  "Content-Type" = "application/json"
}

$sourceFile = [System.IO.Path]::GetTempFileName()
$downloadFile = [System.IO.Path]::GetTempFileName()
$content = "storage smoke $(Get-Date -Format o)"

try {
  Set-Content -Path $sourceFile -Value $content -NoNewline -Encoding utf8

  Write-Host "[storage] upload"
  $uploadUrl = "$supabaseUrl/storage/v1/object/$bucket/$objectPath"
  Invoke-WebRequest -Method POST -Uri $uploadUrl -Headers $uploadHeaders -ContentType "text/plain" -InFile $sourceFile | Out-Null

  Write-Host "[storage] download"
  $downloadUrl = "$supabaseUrl/storage/v1/object/$bucket/$objectPath"
  Invoke-WebRequest -Method GET -Uri $downloadUrl -Headers $downloadHeaders -OutFile $downloadFile | Out-Null

  $downloaded = Get-Content -Path $downloadFile -Raw
  if ($downloaded -ne $content) {
    throw "Downloaded content does not match uploaded content."
  }

  Write-Host "[storage] delete"
  $deleteBody = @{ prefixes = @($objectPath) } | ConvertTo-Json -Compress
  Invoke-WebRequest -Method DELETE -Uri "$supabaseUrl/storage/v1/object/$bucket" -Headers $deleteHeaders -Body $deleteBody | Out-Null

  Write-Host "storage upload/download smoke passed"
}
finally {
  if (Test-Path $sourceFile) { Remove-Item $sourceFile -Force -ErrorAction SilentlyContinue }
  if (Test-Path $downloadFile) { Remove-Item $downloadFile -Force -ErrorAction SilentlyContinue }
}
