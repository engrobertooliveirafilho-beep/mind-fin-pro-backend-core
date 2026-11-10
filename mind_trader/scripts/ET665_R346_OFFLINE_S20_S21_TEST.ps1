$ErrorActionPreference='Stop'
$base='https://raw.githubusercontent.com/engrobertooliveirafilho-beep/mind-fin-pro-backend-core/45fa4580231906bcf76fe87cb406c8ed0da9a8b3'
$root=Join-Path $env:TEMP 'ET665_R346_OFFLINE'
New-Item -ItemType Directory -Force (Join-Path $root 'mind_trader/scripts'),(Join-Path $root 'mind_trader/tests') | Out-Null
foreach($file in @('mind_trader/scripts/et665_r341_s20_s21_causal_gate.py','mind_trader/tests/test_et665_r341_s20_s21_causal_gate.py')){
  Invoke-WebRequest -Uri "$base/$file" -OutFile (Join-Path $root $file)
}
foreach($p in @('mind_trader/__init__.py','mind_trader/scripts/__init__.py','mind_trader/tests/__init__.py')){
  [System.IO.File]::WriteAllText((Join-Path $root $p),'')
}
$previous=$env:PYTHONPATH
$env:PYTHONPATH=$root
try {
  Push-Location $root
  try {
    python -m unittest discover -s mind_trader/tests -t . -p 'test_et665_r341_s20_s21_causal_gate.py' -v
    if($LASTEXITCODE -ne 0){throw "R346 FAIL exit=$LASTEXITCODE"}
    Write-Host 'R346 PASS: S20/S21 unit suite'
  } finally {Pop-Location}
} finally {$env:PYTHONPATH=$previous}
