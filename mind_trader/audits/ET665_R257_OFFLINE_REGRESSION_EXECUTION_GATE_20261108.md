# ET665.R257 — Reproducible offline regression gate

Date: 2026-11-09. Scope: reproducible frozen R257 snapshot at commit `1bdecd9cfa081ac984b8e3da1648544347d9f208` (contains R244–R257). This is an **execution protocol**, not a test result.

## Preconditions (fail closed)
- Operator must have a local checkout at the pinned commit above, with no uncommitted changes. Do not use `main`, production or a live broker environment.
- Docker must already have `python:3.11-slim` cached locally. Do **not** pull an image, enable networking or incur cost.
- Do not pass broker credentials, MT5 terminals, secrets or real order capabilities into the container.
- Test environment must be able to mount the checkout read-only and write temporary files only to a tmpfs.

## PowerShell — single local execution block

```powershell
$ErrorActionPreference='Stop'
$Expected='1bdecd9cfa081ac984b8e3da1648544347d9f208'
$Head=(git rev-parse HEAD).Trim()
if ($Head -ne $Expected) { throw "FAIL_CLOSED: expected $Expected, got $Head" }
if (git status --porcelain) { throw 'FAIL_CLOSED: working tree is dirty' }
$Image='python:3.11-slim'
$Images=docker image inspect $Image 2>$null
if ($LASTEXITCODE -ne 0) { throw 'FAIL_CLOSED: local offline Python image unavailable; no pull permitted' }
$Evidence=Join-Path $env:TEMP ('ET665_R257_'+(Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path $Evidence -Force | Out-Null
git rev-parse HEAD | Set-Content -Path (Join-Path $Evidence 'COMMIT.txt')
docker image inspect $Image --format '{{.Id}}' | Set-Content -Path (Join-Path $Evidence 'IMAGE_ID.txt')
$Repo=(Get-Location).Path
$ArgsList=@('run','--rm','--pull=never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','128','--memory','512m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=64m','--mount',"type=bind,source=$Repo,target=/work,readonly",'--workdir','/work','--env','PYTHONDONTWRITEBYTECODE=1',$Image,'python','-m','unittest','discover','-s','mind_trader/tests/security_review','-p','test_et665_r2*.py','-v')
& docker @ArgsList 2>&1 | Tee-Object -FilePath (Join-Path $Evidence 'TEST_OUTPUT.txt')
$ExitCode=$LASTEXITCODE
"EXIT_CODE=$ExitCode" | Set-Content -Path (Join-Path $Evidence 'RESULT.txt')
Get-FileHash (Join-Path $Evidence 'TEST_OUTPUT.txt') -Algorithm SHA256 | Format-List | Out-String | Set-Content -Path (Join-Path $Evidence 'SHA256.txt')
if ($ExitCode -ne 0) { throw "FAIL_CLOSED: offline regression failed; evidence at $Evidence" }
Write-Output "OFFLINE_REGRESSION_PASS_ONLY (NOT CERTIFICATION): $Evidence"
```

## Interpretation
- `PASS` from this command proves only the discovered `test_et665_r2*.py` unit tests passed in the pinned isolated Python container; it does not certify MT5 isolation, gateway R113, independent promotion, HP19 or all Phase B fronts.
- `FAIL` / missing image / wrong SHA / dirty tree / unavailable Docker blocks progress. Preserve output and SHA-256; never reinterpret as success.
- This runbook was **published but not executed** by the author. No claim of CI/Docker PASS.

`MAIN=INTACTA | PRODUCAO=INTACTA | REAL_ORDERS=FORBIDDEN | FTMO_REAL=FORBIDDEN | COST=R$0`
