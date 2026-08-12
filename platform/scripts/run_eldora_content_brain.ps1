param(
    [switch]$Research,
    [switch]$GenerateOne
)

$ErrorActionPreference = 'Stop'
$Repo = 'C:\Users\MindFin\Desktop\mind-fin-pro-backend-core'
$Python = Join-Path $Repo 'runtime\eldora_media\.venv\Scripts\python.exe'
$Config = Join-Path $Repo 'config\eldora_content_brain\brain.json'
$Canon = Join-Path $Repo 'runtime\eldora_media\canon_cache'
$Downloads = Join-Path $env:USERPROFILE 'Downloads\ELDORA_CONTENT_BRAIN'

Set-Location $Repo

if ($Research) {
    & $Python -m app.eldora_content_brain.cli research --config $Config
    if ($LASTEXITCODE -ne 0) { throw 'CONTENT_RESEARCH=FAIL' }
}

& $Python -m app.eldora_content_brain.cli latest --config $Config
if ($LASTEXITCODE -ne 0) { throw 'LATEST_PLAN=FAIL' }

if ($GenerateOne) {
    $Plan = Get-ChildItem 'runtime\eldora_content_brain\runs' -Recurse -Filter 'research_plan.json' -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $Plan) { throw 'RESEARCH_PLAN_AUSENTE' }

    & $Python -m tools.eldora_content_brain.generate_candidate `
        --plan $Plan.FullName `
        --canon $Canon `
        --downloads $Downloads

    if ($LASTEXITCODE -ne 0) { throw 'CANDIDATE_GENERATION=FAIL' }

    Write-Host "CANDIDATE_DOWNLOADS=$Downloads" -ForegroundColor Green
    Write-Host 'DRIVE_UPLOAD=NAO_EXECUTADO' -ForegroundColor Yellow
    Write-Host 'PUBLICACAO=NAO_EXECUTADA' -ForegroundColor Yellow
}