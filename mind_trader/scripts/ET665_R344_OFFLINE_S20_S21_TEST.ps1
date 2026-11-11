$ErrorActionPreference = 'Stop'

# R346: execute the checked-out source only; no network access or source-tree mutation.
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$sourceModule = Join-Path $PSScriptRoot 'et665_r341_s20_s21_causal_gate.py'
$sourceTests = Join-Path $repoRoot 'mind_trader\tests\test_et665_r341_s20_s21_causal_gate.py'

foreach ($path in @($sourceModule, $sourceTests)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "R346 BLOCKED: required checked-out file missing: $path"
    }
}

$root = Join-Path $env:TEMP 'ET665_R346_OFFLINE'
$moduleDir = Join-Path $root 'mind_trader\scripts'
$testsDir = Join-Path $root 'mind_trader\tests'
New-Item -ItemType Directory -Force $moduleDir, $testsDir | Out-Null

Copy-Item -LiteralPath $sourceModule -Destination (Join-Path $moduleDir 'et665_r341_s20_s21_causal_gate.py') -Force
Copy-Item -LiteralPath $sourceTests -Destination (Join-Path $testsDir 'test_et665_r341_s20_s21_causal_gate.py') -Force

foreach ($path in @(
    (Join-Path $root 'mind_trader\__init__.py'),
    (Join-Path $moduleDir '__init__.py'),
    (Join-Path $testsDir '__init__.py')
)) {
    [System.IO.File]::WriteAllText($path, '')
}

$previous = $env:PYTHONPATH
$env:PYTHONPATH = $root
try {
    Push-Location $root
    try {
        python -m unittest discover -s mind_trader/tests -t . -p 'test_et665_r341_s20_s21_causal_gate.py' -v
        if ($LASTEXITCODE -ne 0) { throw "R346 FAIL exit=$LASTEXITCODE" }
        Write-Host 'R346 PASS: checked-out source, local-only execution'
    } finally {
        Pop-Location
    }
} finally {
    $env:PYTHONPATH = $previous
}
