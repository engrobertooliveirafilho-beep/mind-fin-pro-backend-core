# ET665.R267 — Offline regression execution gate (through R266)

**Frozen tested code:** `42f82f40099fd3c5d7e9bf7a24f645d1634bfd09` (R244–R266). This protocol is published separately from the frozen checkout to avoid self-referential SHA drift. Read the protocol from PR #18; execute against a clean checkout of the exact frozen SHA.

## One PowerShell block

```powershell
$ErrorActionPreference='Stop'
$Expected='42f82f40099fd3c5d7e9bf7a24f645d1634bfd09'
if ((git rev-parse HEAD).Trim() -ne $Expected) { throw 'FAIL_CLOSED: wrong pinned commit' }
if (git status --porcelain) { throw 'FAIL_CLOSED: dirty worktree' }
$Image='python:3.11-slim'
docker image inspect $Image *> $null
if ($LASTEXITCODE -ne 0) { throw 'FAIL_CLOSED: offline image not cached; no pull' }
$Evidence=Join-Path $env:TEMP ('ET665_R267_'+(Get-Date -Format 'yyyyMMdd_HHmmss'))
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
if ($ExitCode -ne 0 -or $Count -eq 0 -or $Log -notmatch '(?m)^OK\s*$') { throw "FAIL_CLOSED: offline regression failed; evidence: $Evidence" }
Write-Output "UNIT_TEST_PASS_ONLY_NOT_CERTIFICATION: $Evidence"
```

## Scope and limitations
All tests matching `test_et665_r2*.py` in the frozen checkout are discovered; test count is measured at execution. No Docker execution is claimed. An offline unit PASS is not independent certification of MT5 isolation, paper gateway, Drive reconciliation or HP19. Docker mounts the checkout read-only; operators must remove secrets and credentials from the checkout before execution. No network, no pulls, no real orders, no production changes, R$0.
