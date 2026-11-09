# ET665.R264 — Offline regression snapshot R244–R263

Date: 2026-11-09. Immutable target commit: `ef97dfd407a500db9900d79edaf7f743b2fd8933`. This snapshot includes the R263 CSV fixture correction. The earlier R257 frozen snapshot does not.

## Single PowerShell command (run only from an authorized local repository checkout)

```powershell
$ErrorActionPreference='Stop'
$Expected='ef97dfd407a500db9900d79edaf7f743b2fd8933'
if ((git rev-parse HEAD).Trim() -ne $Expected) { throw 'FAIL_CLOSED: wrong commit; checkout frozen SHA explicitly' }
if (git status --porcelain) { throw 'FAIL_CLOSED: dirty worktree' }
$Image='python:3.11-slim'
docker image inspect $Image *> $null
if ($LASTEXITCODE -ne 0) { throw 'FAIL_CLOSED: image not cached; no pull permitted' }
$Evidence=Join-Path $env:TEMP ('ET665_R264_'+(Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path $Evidence -Force | Out-Null
$Expected | Set-Content (Join-Path $Evidence 'COMMIT.txt')
docker image inspect $Image --format '{{.Id}}' | Set-Content (Join-Path $Evidence 'IMAGE_ID.txt')
$Repo=(Get-Location).Path
$ArgsList=@('run','--rm','--pull=never','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','128','--memory','512m','--cpus','1','--tmpfs','/tmp:rw,noexec,nosuid,size=64m','--mount',"type=bind,source=$Repo,target=/work,readonly",'--workdir','/work','--env','PYTHONDONTWRITEBYTECODE=1',$Image,'python','-m','unittest','discover','-s','mind_trader/tests/security_review','-p','test_et665_r2*.py','-v')
& docker @ArgsList *> (Join-Path $Evidence 'TEST_OUTPUT.txt')
$ExitCode=$LASTEXITCODE
$Log=Get-Content (Join-Path $Evidence 'TEST_OUTPUT.txt') -Raw
$Match=[regex]::Match($Log,'Ran\s+(\d+)\s+tests?\s+in\s+')
$Count=if ($Match.Success) { [int]$Match.Groups[1].Value } else { 0 }
"DISCOVERED_TESTS=$Count" | Set-Content (Join-Path $Evidence 'TEST_COUNT.txt')
"EXIT_CODE=$ExitCode" | Set-Content (Join-Path $Evidence 'RESULT.txt')
Get-FileHash (Join-Path $Evidence 'TEST_OUTPUT.txt') -Algorithm SHA256 | Format-List | Out-String | Set-Content (Join-Path $Evidence 'SHA256.txt')
if ($ExitCode -ne 0 -or $Count -eq 0 -or $Log -notmatch '(?m)^OK\s*$') { throw "FAIL_CLOSED: test failure or missing positive evidence; $Evidence" }
Write-Output "UNIT_TEST_PASS_ONLY_NOT_CERTIFICATION: $Evidence"
```

## Evidence boundary
The PR currently contains 11 `test_et665_r2*.py` files, but the number of discovered methods and their outcome must be measured by this command, not assumed. No Docker test has been executed here. A successful unit-test run does not certify MT5 isolation, R113, R60, HP19 or Phase B. No merge, deployment, broker credentials or real orders; COST=R$0.
