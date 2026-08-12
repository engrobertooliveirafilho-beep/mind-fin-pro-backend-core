$ErrorActionPreference = "Stop"

$ROOT = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core"
$OUT = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P2264B_P2266_FULL_DATA_BACKTEST_PIPELINE_20260618_162142"
$common = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"

$files = Get-ChildItem $common -Filter "mind_dataset_*.csv" -ErrorAction SilentlyContinue

if (-not $files) {
    throw "Nenhum mind_dataset_*.csv encontrado em Common\Files."
}

$ready = @()

foreach ($f in $files) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
    $clean = $base -replace "^mind_dataset_",""
    $parts = $clean -split "_"

    if ($parts.Count -lt 2) { continue }

    $tf = $parts[-1]
    $symbol = ($parts[0..($parts.Count-2)] -join "_")

    $rows = (Get-Content $f.FullName | Measure-Object -Line).Lines

    if ($rows -gt 100) {
        $destDir = Join-Path $OUT "datasets_ready\$symbol"
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null

        $dest = Join-Path $destDir $f.Name
        Copy-Item $f.FullName $dest -Force

        $ready += [pscustomobject]@{
            symbol = $symbol
            timeframe = $tf
            rows = $rows
            source = $f.FullName
            dataset_file = $dest
            status = "READY_BACKTEST"
        }
    }
}

$readyCsv = Join-Path $OUT "datasets_ready\p2264b_ready_datasets.csv"
$ready | Export-Csv $readyCsv -NoTypeInformation -Encoding UTF8

Write-Host "[OK] READY DATASETS:" $ready.Count
Write-Host "[OK] MANIFEST:" $readyCsv
