param(
  [string]$ApiBaseUrl = "http://10.0.2.2:8000",
  [string]$EnvFile = ".env",
  [string[]]$DeviceId,
  [switch]$Android,
  [switch]$Windows,
  [switch]$Edge,
  [switch]$PrintOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$preferredAndroidDeviceId = "RFCR80K8WQV"

$repoRoot = Split-Path -Parent $PSScriptRoot
$mobileDir = Join-Path $repoRoot "mobile"

$resolvedEnvFile = if ([System.IO.Path]::IsPathRooted($EnvFile)) {
  $EnvFile
} else {
  Join-Path $repoRoot $EnvFile
}

if (-not (Test-Path $resolvedEnvFile)) {
  throw "Env file not found: $resolvedEnvFile"
}

$lines = Get-Content $resolvedEnvFile

function Get-EnvValue([string]$key) {
  $line = $lines |
    Where-Object { $_ -match ("^" + [regex]::Escape($key) + "=") } |
    Select-Object -First 1
  if ($null -eq $line) {
    throw "Missing key in env file '$resolvedEnvFile': $key"
  }
  return $line.Substring($key.Length + 1).Trim()
}

$supabaseUrl = Get-EnvValue "SUPABASE_URL"
$supabaseAnonKey = Get-EnvValue "SUPABASE_ANON_KEY"

if ([string]::IsNullOrWhiteSpace($supabaseUrl) -or $supabaseUrl -eq "replace_me") {
  throw "SUPABASE_URL is empty/placeholder in $resolvedEnvFile"
}

if ([string]::IsNullOrWhiteSpace($supabaseAnonKey) -or $supabaseAnonKey -eq "replace_me") {
  throw "SUPABASE_ANON_KEY is empty/placeholder in $resolvedEnvFile"
}

Write-Host "Detecting Flutter devices..." -ForegroundColor Cyan
$devices = flutter devices --machine | ConvertFrom-Json

$selectedDevices = @()

if ($DeviceId -and $DeviceId.Count -gt 0) {
  $selectedDevices = @(
    $devices | Where-Object { $DeviceId -contains $_.id }
  )
} else {
  $useExplicitFlags = $Android.IsPresent -or $Windows.IsPresent -or $Edge.IsPresent
  if ($useExplicitFlags) {
    if ($Android) {
      $preferredAndroid = @(
        $devices | Where-Object { $_.isSupported -eq $true -and $_.id -eq $preferredAndroidDeviceId }
      )
      if ($preferredAndroid.Count -eq 0) {
        throw "Preferred Android device '$preferredAndroidDeviceId' not found. Run 'flutter devices' or use -DeviceId."
      }
      $selectedDevices += $preferredAndroid
    }
    if ($Windows) {
      $selectedDevices += @(
        $devices | Where-Object { $_.isSupported -eq $true -and $_.id -eq "windows" }
      )
    }
    if ($Edge) {
      $selectedDevices += @(
        $devices | Where-Object { $_.isSupported -eq $true -and $_.id -eq "edge" }
      )
    }
  } else {
    $selectedDevices = @(
      $devices | Where-Object {
        $_.isSupported -eq $true -and (
          $_.targetPlatform -like "android-*" -or
          $_.id -eq "windows" -or
          $_.id -eq "edge"
        )
      }
    )
  }
}

$selectedDevices = @($selectedDevices | Group-Object -Property id | ForEach-Object { $_.Group[0] })

if ($selectedDevices.Count -eq 0) {
  throw "No matching devices found. Run 'flutter devices' and adjust flags or -DeviceId."
}

foreach ($device in $selectedDevices) {
  $apiBaseUrlForDevice = if ($device.id -eq "edge") {
    "http://localhost:8000"
  } else {
    $ApiBaseUrl
  }

  $flutterArgs = @(
    "run",
    "-d", $device.id,
    "--dart-define=SUPABASE_URL=$supabaseUrl",
    "--dart-define=SUPABASE_ANON_KEY=$supabaseAnonKey",
    "--dart-define=API_BASE_URL=$apiBaseUrlForDevice"
  )

  $safePreview = @(
    "run",
    "-d", $device.id,
    "--dart-define=SUPABASE_URL=$supabaseUrl",
    "--dart-define=SUPABASE_ANON_KEY=***REDACTED***",
    "--dart-define=API_BASE_URL=$apiBaseUrlForDevice"
  )

  $command = "flutter $($flutterArgs -join ' ')"

  Write-Host "Starting on $($device.name) ($($device.id))" -ForegroundColor Green
  Write-Host ("flutter " + ($safePreview -join " ")) -ForegroundColor DarkGray

  if (-not $PrintOnly) {
    Start-Process powershell `
      -WorkingDirectory $mobileDir `
      -ArgumentList "-NoExit", "-Command", $command | Out-Null
  }
}
