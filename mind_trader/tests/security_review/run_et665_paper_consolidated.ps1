# ET665 PAPER consolidated regression (offline, fail closed, no production)
param([string]$Evidence='D:\MIND_TEMP\ET665_PAPER_RECOVERY\evidence\R_TRANSACTIONAL_20261111_193051')
$ErrorActionPreference='Stop'
$repo=(git rev-parse --show-toplevel).Trim()
if($LASTEXITCODE -ne 0){throw 'NOT_A_GIT_REPOSITORY'}
Set-Location $repo
$branch=(git branch --show-current).Trim()
if($branch -eq 'main' -or $branch -eq 'master'){throw 'PROTECTED_BRANCH'}
$modules=@(
'mind_trader.tests.security_review.test_et665_paper_idempotency',
'mind_trader.tests.security_review.test_et665_paper_reconciliation',
'mind_trader.tests.security_review.test_et665_gateway_crash_windows',
'mind_trader.tests.security_review.test_et665_transactional_recovery',
'mind_trader.tests.security_review.test_et665_r313_paper_adversarial',
'mind_trader.tests.security_review.test_et665_r314_gateway_broker_contract',
'mind_trader.tests.security_review.test_et665_i_gateway_broker_rejection',
'mind_trader.tests.security_review.test_et665_bw_gateway_malformed_inputs',
'mind_trader.tests.security_review.test_et665_mb_r4_paper_session_corruption',
'mind_trader.tests.security_review.test_et665_mb_r5_paper_pnl_integrity',
'mind_trader.tests.security_review.test_et665_mb_r6_paper_fill_safety'
)
$stamp=Get-Date -Format 'yyyyMMdd_HHmmss'
$out=Join-Path 'D:\MIND_TEMP' "ET665_PAPER_CONSOLIDATED\$stamp"
New-Item -ItemType Directory -Force -Path $out | Out-Null
$report=[ordered]@{mission='ET665.PAPER.CONSOLIDATED';timestamp=(Get-Date).ToString('o');branch=$branch;commit=(git rev-parse HEAD).Trim();evidence=$Evidence;integrity='NOT_VERIFIED';tests='NOT_RUN';e2e_certified=$false;production_modified=$false;files=@()}
try {
 if(!(Test-Path -LiteralPath $Evidence -PathType Container)){throw 'EVIDENCE_DIRECTORY_NOT_FOUND'}
 $evfiles=@(Get-ChildItem -LiteralPath $Evidence -Recurse -File)
 if($evfiles.Count -eq 0){throw 'EVIDENCE_EMPTY'}
 foreach($f in $evfiles){
  $report.files+=@{relative=$f.FullName.Substring($Evidence.Length).TrimStart('\');size=$f.Length;sha256=(Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256).Hash}
 }
 $report.integrity='FILES_HASHED_ONLY_NO_AUTHORITY_COMPARISON'
 $env:PYTHONDONTWRITEBYTECODE='1'
 $env:PYTHONNOUSERSITE='1'
 $env:PAPER_ONLY='1'
 $env:REAL_ORDERS='FORBIDDEN'
 $env:FTMO_REAL='FORBIDDEN'
 & python -m unittest -v @modules 2>&1 | Tee-Object -FilePath (Join-Path $out 'unittest.log')
 $code=$LASTEXITCODE
 if($code -ne 0){throw "REGRESSION_FAILED_EXIT_$code"}
 $report.tests='PASS'
} catch {
 $report.error=$_.Exception.Message
 $report.tests=if($report.tests -eq 'PASS'){'PASS'}else{'FAIL_OR_NOT_RUN'}
 throw
} finally {
 $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'report.json') -Encoding UTF8
 Write-Host "EVIDENCE=$out"
 Write-Host "INTEGRITY=$($report.integrity) | TESTS=$($report.tests) | E2E_CERTIFIED=FALSE | PAPER_ONLY | R$0"
}
