param(
  [string]$HistoricalCsv = '',
  [string]$IndependentSha256 = ''
)
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$root=Join-Path $env:TEMP ('ET665_R347_VERIFIED_' + [guid]::NewGuid().ToString('N'))
$module=Join-Path $root 'mind_trader\scripts'
$tests=Join-Path $root 'mind_trader\tests'
$evidence=Join-Path $root 'EVIDENCE'
New-Item -ItemType Directory -Force $module,$tests,$evidence | Out-Null
$blobs=[ordered]@{
  'mind_trader/scripts/et665_r341_s20_s21_causal_gate.py'='2022b8b4d0b57bda7ce91557faf3c0118824b34c'
  'mind_trader/scripts/et665_r347_real_component_e2e.py'='6de1cc19718df772c62f0f3fc311e828683838a1'
  'mind_trader/tests/test_et665_r347_real_component_e2e.py'='de9713f378b887bb4dfa7485469b7e9a5e93afd0'
}
Push-Location $repo
try {
  foreach($entry in $blobs.GetEnumerator()){
    $p=$entry.Key
    if(!(Test-Path -LiteralPath $p -PathType Leaf)){throw "SOURCE_MISSING:$p"}
    $actual=(& git hash-object -- $p).Trim()
    if($LASTEXITCODE -ne 0 -or $actual -ne $entry.Value){throw "GIT_BLOB_MISMATCH:$p expected=$($entry.Value) actual=$actual"}
    $dest=Join-Path $root ($p -replace '/','\')
    Copy-Item -LiteralPath $p -Destination $dest -Force
  }
  $p='mind_trader/tests/test_et665_r341_s20_s21_causal_gate.py'
  if(!(Test-Path -LiteralPath $p -PathType Leaf)){throw "SOURCE_MISSING:$p"}
  Copy-Item -LiteralPath $p -Destination (Join-Path $tests 'test_et665_r341_s20_s21_causal_gate.py') -Force
} finally {Pop-Location}
foreach($p in @((Join-Path $root 'mind_trader\__init__.py'),(Join-Path $module '__init__.py'),(Join-Path $tests '__init__.py'))){
  [IO.File]::WriteAllText($p,'')
}
$old=$env:PYTHONPATH
$env:PYTHONPATH=$root
try {
  Push-Location $root
  try {
    & python -m unittest mind_trader.tests.test_et665_r341_s20_s21_causal_gate mind_trader.tests.test_et665_r347_real_component_e2e -v 2>&1 | Tee-Object -FilePath (Join-Path $evidence 'unittest.log')
    if($LASTEXITCODE -ne 0){throw "R347_TEST_FAIL:$LASTEXITCODE"}
    $blobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $evidence 'verified_git_blobs.json') -Encoding utf8
    if($HistoricalCsv){
      if($IndependentSha256 -notmatch '^[0-9a-f]{64}$'){throw 'INDEPENDENT_SHA256_REQUIRED'}
      $csv=(Resolve-Path -LiteralPath $HistoricalCsv).Path
      & python -m mind_trader.scripts.et665_r347_real_component_e2e $csv --expected-sha256 $IndependentSha256 --evidence (Join-Path $evidence 'historical.json') 2>&1 | Tee-Object -FilePath (Join-Path $evidence 'historical.log')
      if($LASTEXITCODE -ne 0){throw "R347_HISTORICAL_FAIL:$LASTEXITCODE"}
    }
    Write-Host "R347_VERIFIED_TESTS_PASS evidence=$evidence"
  } finally {Pop-Location}
} finally {$env:PYTHONPATH=$old}
