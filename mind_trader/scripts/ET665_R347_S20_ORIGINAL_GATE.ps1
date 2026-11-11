param(
  [string]$Workspace='D:\MIND_TEMP\ELDORA_TRADER_ACTIVE_WORKSPACE',
  [string]$ExpectedSha256='f1bc79d66985e0e9d776239b4c44e613574530a0b34e989d34eecffa88083bf7'
)
$ErrorActionPreference='Stop'
$run='S20_20260806_195027'
$ledger=Join-Path $Workspace "runs\$run\ledgers\S20_DECISION_LEDGER.csv"
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$evidence=Join-Path $env:TEMP ('ET665_R347_S20_ORIGINAL_'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $evidence -Force | Out-Null
$report=[ordered]@{mission='ET665.R347';mode='PAPER_ONLY';status='BLOCKED';source=$ledger;expected_sha256=$ExpectedSha256;actual_sha256=$null;schema=$null;reason=$null;runtime_log=$null}
try {
  if(!(Test-Path -LiteralPath $ledger -PathType Leaf)){throw 'ORIGINAL_S20_LEDGER_NOT_FOUND'}
  $actual=(Get-FileHash -LiteralPath $ledger -Algorithm SHA256).Hash.ToLowerInvariant()
  $report.actual_sha256=$actual
  if($actual -ne $ExpectedSha256){throw 'ORIGINAL_S20_LEDGER_SHA256_MISMATCH'}
  $header=[IO.File]::ReadLines($ledger) | Select-Object -First 1
  $report.schema=$header
  $required=@('decision_id','strategy_id','symbol','decision_ts','signal_ts','price_ts','price','source_sha256')
  $fields=@($header.TrimStart([char]0xFEFF).Split(',') | ForEach-Object {$_.Trim('"')})
  if((@($fields | Sort-Object) -join '|') -ne (@($required | Sort-Object) -join '|')){throw 'S20_ORIGINAL_SCHEMA_NOT_R347_COMPATIBLE'}
  $runner=Join-Path $repo 'mind_trader\scripts\ET665_R347_OFFLINE_E2E_TEST.ps1'
  if(!(Test-Path -LiteralPath $runner)){throw 'R347_EXISTING_RUNNER_MISSING'}
  $log=Join-Path $evidence 'runtime.log'
  & $runner -HistoricalCsv $ledger -IndependentSha256 $actual *>&1 | Out-File -FilePath $log -Encoding utf8
  $report.runtime_log=$log
  if(!$?){throw 'R347_RUNTIME_FAIL'}
  $report.status='STRUCTURAL_ONLY_NOT_OOS_CERTIFIED'
  $report.reason='R347_RUNNER_RETURNED_SUCCESS'
} catch {
  $report.reason=$_.Exception.Message
} finally {
  $report | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $evidence 's20_gate.json') -Encoding utf8
  Write-Output ($report | ConvertTo-Json -Compress)
  Write-Output "EVIDENCE_DIR=$evidence"
}
if($report.status -eq 'BLOCKED'){exit 2}
