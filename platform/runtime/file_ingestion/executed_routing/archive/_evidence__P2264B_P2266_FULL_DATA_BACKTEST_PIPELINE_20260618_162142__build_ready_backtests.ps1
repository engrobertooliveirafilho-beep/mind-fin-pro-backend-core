$ErrorActionPreference = "Stop"

$OUT = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P2264B_P2266_FULL_DATA_BACKTEST_PIPELINE_20260618_162142"
$queuePath = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P2263_STRATEGY_MUTATION_20260618_151114\backtest_queue\p2263_mutation_backtest_queue.csv"
$readyPath = Join-Path $OUT "datasets_ready\p2264b_ready_datasets.csv"

if (-not (Test-Path $readyPath)) {
    throw "Ready datasets não encontrado. Rode sync_mt5_datasets.ps1 primeiro."
}

$queue = Import-Csv $queuePath
$ready = Import-Csv $readyPath

$readyMap = @{}
foreach ($r in $ready) {
    $key = "$($r.symbol)|$($r.timeframe)"
    $readyMap[$key] = $r.dataset_file
}

$btReady = @()
$blocked = @()

foreach ($q in $queue) {
    $key = "$($q.symbol)|$($q.timeframe)"

    if ($readyMap.ContainsKey($key)) {
        $q.status = "READY_BACKTEST"
        $q.dataset_file = $readyMap[$key]
        $btReady += $q
    } else {
        $q.status = "BLOCKED_NO_DATA"
        $blocked += $q
    }
}

$btReadyCsv = Join-Path $OUT "backtest_ready\p2264c_ready_backtests.csv"
$blockedCsv = Join-Path $OUT "backtest_ready\p2264c_blocked_backtests.csv"

$btReady | Export-Csv $btReadyCsv -NoTypeInformation -Encoding UTF8
$blocked | Export-Csv $blockedCsv -NoTypeInformation -Encoding UTF8

Write-Host "[OK] READY_BACKTEST:" $btReady.Count
Write-Host "[OK] BLOCKED:" $blocked.Count
Write-Host "[OK] READY FILE:" $btReadyCsv
