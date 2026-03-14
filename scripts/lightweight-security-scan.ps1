$ErrorActionPreference = "Stop"

$trackedFiles = git ls-files
$patterns = @(
  @{ Name = "openai_api_key"; Regex = "sk-[A-Za-z0-9]{20,}" },
  @{ Name = "aws_access_key"; Regex = "AKIA[0-9A-Z]{16}" },
  @{ Name = "github_pat"; Regex = "github_pat_[A-Za-z0-9_]{20,}" }
)

$violations = New-Object System.Collections.Generic.List[string]

foreach ($file in $trackedFiles) {
  if (-not (Test-Path $file)) {
    continue
  }

  $lineNumber = 0
  Get-Content $file | ForEach-Object {
    $lineNumber += 1
    foreach ($pattern in $patterns) {
      if ($_ -match $pattern.Regex) {
        $violations.Add("${file}:$lineNumber matched $($pattern.Name)")
      }
    }
  }
}

if ($violations.Count -gt 0) {
  Write-Host "security scan violations:"
  $violations | ForEach-Object { Write-Host $_ }
  throw "lightweight security scan failed"
}

Write-Host "lightweight security scan passed"
