$ErrorActionPreference = "Stop"

$extensions = @(".py", ".ps1", ".md", ".yaml", ".yml", ".dart", ".toml", ".json", ".ini", ".txt", ".sh")
$files = git ls-files | Where-Object {
  $ext = [System.IO.Path]::GetExtension($_).ToLowerInvariant()
  $extensions -contains $ext
} | Where-Object {
  $_ -notmatch '^(docs|specs|ADR)/'
}

$violations = New-Object System.Collections.Generic.List[string]

foreach ($file in $files) {
  if (-not (Test-Path $file)) {
    continue
  }

  $lineNumber = 0
  Get-Content $file | ForEach-Object {
    $lineNumber += 1
    if ($_ -match "\s+$") {
      $violations.Add("${file}:$lineNumber trailing whitespace")
    }
    if ($_ -match "`t") {
      $violations.Add("${file}:$lineNumber tab character")
    }
  }
}

if ($violations.Count -gt 0) {
  Write-Host "format check violations:"
  $violations | ForEach-Object { Write-Host $_ }
  throw "format checks failed"
}

Write-Host "format checks passed"
