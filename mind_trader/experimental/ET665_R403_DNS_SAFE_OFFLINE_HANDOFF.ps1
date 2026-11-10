# ET665.R403 — DNS-safe offline handoff (PowerShell 7)
# Execute from any folder. Never changes production or main.
$ErrorActionPreference = 'Stop'
$root = 'D:\MIND_TEMP\ET665_R348_TEST_WORKSPACE'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$evidence = Join-Path $root "R403_$stamp"
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$report = [ordered]@{period_id=$stamp; dns='UNKNOWN'; https='UNKNOWN'; local_repo='UNKNOWN'; tests='NOT_RUN'; official_hp19_certified=0; phase_b_certified=0; paper_only=$true}
try {
  $ips = @(Resolve-DnsName github.com -Type A -ErrorAction Stop | Where-Object IPAddress | Select-Object -ExpandProperty IPAddress)
  if ($ips.Count -eq 0) { throw 'DNS_EMPTY' }
  $report.dns = 'PASS'
} catch { $report.dns = 'FAIL'; $report.dns_error = $_.Exception.Message }
try {
  if ($report.dns -eq 'PASS') {
    $response = Invoke-WebRequest 'https://github.com' -Method Head -TimeoutSec 10 -UseBasicParsing
    $report.https = "HTTP_$($response.StatusCode)"
  } else { $report.https = 'BLOCKED_BY_DNS' }
} catch { $report.https = 'FAIL'; $report.https_error = $_.Exception.Message }
$repo = Join-Path $root 'mind-fin-pro-backend-core'
if (Test-Path (Join-Path $repo '.git')) {
  $report.local_repo = 'PRESENT'
  $head = git -C $repo rev-parse HEAD 2>&1
  if ($LASTEXITCODE -eq 0) { $report.head = "$head" }
  $testFile = Join-Path $repo 'mind_trader\tests\security_review\test_et665_r400_docker_component_runner.py'
  if (Test-Path $testFile) {
    Push-Location $repo
    try {
      $env:PYTHONDONTWRITEBYTECODE = '1'
      $env:PYTHONPATH = $repo
      $log = Join-Path $evidence 'r403_unittest.log'
      & python -B -m unittest mind_trader.tests.security_review.test_et665_r400_docker_component_runner -v *> $log
      $report.tests = if ($LASTEXITCODE -eq 0) { 'PASS' } else { 'FAIL' }
      $report.test_log_sha256 = (Get-FileHash $log -Algorithm SHA256).Hash
    } finally { Pop-Location }
  } else { $report.tests = 'MISSING_LOCAL_TESTS' }
} else { $report.local_repo = 'ABSENT'; $report.tests = 'BLOCKED_NO_LOCAL_REPO' }
$report | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $evidence 'r403_report.json') -Encoding utf8
Get-Content (Join-Path $evidence 'r403_report.json')
# No clone, pull, checkout, merge, or real orders.
