# ET665.R337 — Windows PowerShell 5.1+ offline Docker verification
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File .\mind_trader\tools\et665_r337_offline_docker_regression.ps1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = (& git rev-parse --show-toplevel)
if ($LASTEXITCODE -ne 0 -or -not $root) { throw 'FAIL_CLOSED: repository not found' }
$root = $root.Trim()
Set-Location $root
$dirty = @(& git status --porcelain)
if ($LASTEXITCODE -ne 0 -or $dirty.Count -gt 0) { throw 'FAIL_CLOSED: worktree must be clean' }
& docker image inspect python:3.11 *> $null
if ($LASTEXITCODE -ne 0) { throw 'FAIL_CLOSED: cached python:3.11 unavailable; no pull attempted' }
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss')
$evidence = Join-Path ([System.IO.Path]::GetTempPath()) ("ET665_R337_" + $stamp)
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
(& git rev-parse HEAD) | Set-Content -Encoding ASCII (Join-Path $evidence 'commit.txt')
$paths = @(
 'mind_trader/app/p1519_p1525_institutional_research_certification/engine.py',
 'mind_trader/tests/security_review/test_et665_r332_causal_fill_gate.py',
 'mind_trader/tests/security_review/test_et665_r334_synthetic_reconstruction_e2e.py',
 'mind_trader/tests/security_review/test_et665_r338_report_pipeline_e2e.py'
)
$paths | ForEach-Object {
 $hash = Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $_)
 "$($hash.Hash)  $_"
} | Set-Content -Encoding ASCII (Join-Path $evidence 'source_sha256.txt')
$log = Join-Path $evidence 'unittest.log'
# Docker image must already be cached; network is always disabled.
& docker run --rm --pull never --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 --memory 256m --cpus 1 --tmpfs /tmp:rw,noexec,nosuid,size=32m --mount "type=bind,src=$root,dst=/work,readonly" --workdir /work python:3.11 python -B -m unittest -v mind_trader/tests/security_review/test_et665_r332_causal_fill_gate.py mind_trader/tests/security_review/test_et665_r334_synthetic_reconstruction_e2e.py mind_trader/tests/security_review/test_et665_r338_report_pipeline_e2e.py 2>&1 | Tee-Object -FilePath $log
$exitCode = $LASTEXITCODE
"$exitCode" | Set-Content -Encoding ASCII (Join-Path $evidence 'exit_code.txt')
Get-ChildItem -File $evidence | Sort-Object Name | ForEach-Object {
 $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName
 "$($hash.Hash)  $($_.Name)"
} | Set-Content -Encoding ASCII (Join-Path $evidence 'evidence_sha256.txt')
Write-Host "EVIDENCE=$evidence"
if ($exitCode -ne 0) { throw "R337=FAIL_CLOSED EXIT_CODE=$exitCode" }
Write-Host 'R337=REGRESSIONS_PASS_ONLY; HP19=NOT_CERTIFIED; PHASE_B=NOT_CERTIFIED'
