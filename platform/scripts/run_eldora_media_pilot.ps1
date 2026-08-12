param(
    [int]$Count = 1,
    [switch]$Produce
)

$ErrorActionPreference = 'Stop'
$Repo = 'C:\Users\MindFin\Desktop\mind-fin-pro-backend-core'
$Python = Join-Path $Repo 'runtime\eldora_media\.venv\Scripts\python.exe'
$Config = Join-Path $Repo 'config\eldora_media\eldora_media.json'

if (-not (Test-Path $Python)) { throw 'VENV_AUSENTE_EXECUTE_ELDORA.MEDIA.002_-InstallDeps' }

$env:ELDORA_IMAGE_GENERATOR_CMD = "`"$Python`" -m tools.eldora_media.openai_image_adapter --prompt-file `"{prompt_file}`" --reference-dir `"{reference_dir}`" --output-dir `"{output_dir}`" --content-id `"{content_id}`""
$env:ELDORA_IDENTITY_VALIDATOR_CMD = "`"$Python`" -m tools.eldora_media.insightface_validator --candidate `"{candidate}`" --reference-dir `"{reference_dir}`" --report-file `"{report_file}`""

Set-Location $Repo

if ($Produce) {
    & $Python -m app.eldora_media_runtime.cli produce --count $Count --config $Config
} else {
    & $Python -m app.eldora_media_runtime.cli audit --config $Config
}