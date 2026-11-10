# ET665.R346 real-module gate: Docker offline, no mocks, no orders.
$ErrorActionPreference = 'Stop'
$root = (& git rev-parse --show-toplevel).Trim()
if ($LASTEXITCODE -ne 0 -or -not $root) { throw 'FAIL_CLOSED: git checkout missing' }
$dirty = @(& git -C $root status --porcelain)
if ($dirty.Count -gt 0) { throw 'FAIL_CLOSED: dirty worktree' }
& docker image inspect python:3.11 *> $null
if ($LASTEXITCODE -ne 0) { throw 'FAIL_CLOSED: cached python:3.11 image missing' }
$evidence = Join-Path ([IO.Path]::GetTempPath()) ('ET665_R346_' + (Get-Date -Format yyyyMMdd_HHmmss))
New-Item -ItemType Directory -Path $evidence | Out-Null
(& git -C $root rev-parse HEAD) | Set-Content -Encoding ASCII (Join-Path $evidence 'commit.txt')
& docker run --rm --pull never --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 --memory 256m --cpus 1 --tmpfs /tmp:rw,noexec,nosuid,size=32m --mount "type=bind,src=$root,dst=/work,readonly" --mount "type=bind,src=$evidence,dst=/evidence" --workdir /work python:3.11 python -B mind_trader/experimental/et665_r346_real_agent_gate.py --evidence /evidence 2>&1 | Tee-Object -FilePath (Join-Path $evidence 'execution.log')
$code = $LASTEXITCODE
"$code" | Set-Content -Encoding ASCII (Join-Path $evidence 'exit_code.txt')
Get-ChildItem -File $evidence | Sort-Object Name | ForEach-Object { "$((Get-FileHash $_.FullName -Algorithm SHA256).Hash)  $($_.Name)" } | Set-Content -Encoding ASCII (Join-Path $evidence 'sha256.txt')
Write-Host "EVIDENCE=$evidence"
if ($code -ne 0) { throw 'R346=FAIL_CLOSED; real 19-agent proof not obtained' }
Write-Host 'R346=19_CANDIDATE_MODULES_VERIFIED_ONLY; HP19 membership still unverified'
