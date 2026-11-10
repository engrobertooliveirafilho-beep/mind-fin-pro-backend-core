# ET665.R334 — Offline combined regression runner (research only)
# Execute on operator Windows PC with Docker already installed; no network in container.
# Pins source to R334 test commit, checks integrity, uses readonly workspace, tmpfs for tempfile.
# No merge, no production, no broker, no real orders.
$ErrorActionPreference = 'Stop'
$repo = 'https://github.com/engrobertooliveirafilho-beep/mind-fin-pro-backend-core.git'
$sha = '52f5d1897dc8939fc52eddd5e8f2abc83b78a719'
# Clone into a fresh unique directory. Never reuse or overwrite prior evidence/source.
$runId = (Get-Date).ToUniversalTime().ToString('yyyyMMdd_HHmmss_fff') + '_' + [guid]::NewGuid().ToString('N').Substring(0,8)
$root = Join-Path 'D:\MIND_TEMP\ET665_R330_OFFLINE_REGRESSION' $runId
$src = Join-Path $root 'source'
$evidence = Join-Path $root 'EVIDENCE'
New-Item -ItemType Directory -Path $root,$evidence | Out-Null
git clone --no-checkout $repo $src
if ($LASTEXITCODE -ne 0) { throw 'clone failed' }
git -C $src fetch origin $sha
if ($LASTEXITCODE -ne 0) { throw 'fetch failed' }
# Checkout is safe here because this is a newly created, exclusive clone.
git -C $src checkout --detach $sha
if ($LASTEXITCODE -ne 0) { throw 'checkout failed' }
$dirty = git -C $src status --porcelain
if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'source dirty after checkout; aborting' }
$actual = (git -C $src rev-parse HEAD).Trim()
if ($actual -ne $sha) { throw "unexpected commit $actual" }
$tests = @('tests/test_et665_r326_causal_walk_forward.py','tests/test_et665_r328_causal_oos_costs.py')
# Refuse stale/incorrect test imports before starting Docker.
$testText = Get-Content (Join-Path $src 'tests/test_et665_r328_causal_oos_costs.py') -Raw
if ($testText -match 'evaluate_causal_oos_csv' -or $testText -notmatch 'evaluate_cost_aware_oos_csv') { throw 'R328 test/API mismatch; aborting' }
foreach ($p in $tests) { if (-not (Test-Path (Join-Path $src $p))) { throw "missing $p" } }
$files = @('mind_trader/research/et665_r326_causal_walk_forward.py','mind_trader/research/et665_r315_immutable_csv_snapshot.py','mind_trader/research/et665_r328_causal_oos_costs.py') + $tests
Get-Item ($files | ForEach-Object { Join-Path $src $_ }) | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $evidence 'SOURCE_HASHES.json') -Encoding UTF8
$stamp = (Get-Date).ToUniversalTime().ToString('o')
@{r='R334';commit=$actual;started_utc=$stamp;docker_image='python:3.11';network='none';read_only=$true;privileges='no-new-privileges';paper_only=$true} | ConvertTo-Json | Set-Content (Join-Path $evidence 'MANIFEST.json') -Encoding UTF8
docker image inspect python:3.11 *> $null
if ($LASTEXITCODE -ne 0) { throw 'python:3.11 image absent; offline test aborted (no pull)' }
$log = Join-Path $evidence 'PYTEST.log'
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --pids-limit 128 --memory 512m --cpus 1 --tmpfs /tmp:rw,noexec,nosuid,size=64m -v "${src}:/work:ro" -w /work -e PYTHONDONTWRITEBYTECODE=1 -e PYTHONPATH=/work python:3.11 python -m unittest -v tests.test_et665_r326_causal_walk_forward tests.test_et665_r328_causal_oos_costs 2>&1 | Tee-Object -FilePath $log
$exit = $LASTEXITCODE
@{r='R330';exit_code=$exit;completed_utc=(Get-Date).ToUniversalTime().ToString('o');source_commit=$actual;expected_tests=45;scope='unittest regression only, no market evidence, no certification'} | ConvertTo-Json | Set-Content (Join-Path $evidence 'RESULT.json') -Encoding UTF8
Get-ChildItem -File $evidence | Where-Object Name -ne 'EVIDENCE_SHA256.csv' | Get-FileHash -Algorithm SHA256 | Select-Object Path,Hash | Export-Csv (Join-Path $evidence 'EVIDENCE_SHA256.csv') -NoTypeInformation -Encoding UTF8
Write-Host "R338 EXIT=$exit EVIDENCE=$evidence"
if ($exit -ne 0) { throw 'regressions failed; do not certify' }
