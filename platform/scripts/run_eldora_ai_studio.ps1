param(
    [ValidateSet('audit','research','generate','latest')]
    [string]$Mode = 'audit'
)

$ErrorActionPreference = 'Stop'
$Repo = 'C:\Users\MindFin\Desktop\mind-fin-pro-backend-core'
$Python = Join-Path $Repo 'runtime\eldora_media\.venv\Scripts\python.exe'
$Config = Join-Path $Repo 'config\eldora_ai_studio\studio.json'

Set-Location $Repo

& $Python -m app.eldora_ai_studio.cli $Mode --config $Config
if ($LASTEXITCODE -ne 0) {
    throw "ELDORA_AI_STUDIO_$($Mode.ToUpper())=FAIL"
}