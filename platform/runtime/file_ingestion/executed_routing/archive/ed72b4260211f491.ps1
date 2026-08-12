$ErrorActionPreference = "Stop"

$signalPlan = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P2264B_P2266_FULL_DATA_BACKTEST_PIPELINE_20260618_162142\edge_ranking\P2266_P2270_PAPER_PORTFOLIO_EDGE_PACK_20260619_152952\mt5_signal_plan\mt5_signal_plan.csv"
$edges = Import-Csv $signalPlan

$common = Join-Path $env:APPDATA "MetaQuotes\Terminal\Common\Files"
New-Item -ItemType Directory -Force -Path $common | Out-Null

$orderFile = Join-Path $common "mt5_order.txt"
$logFile = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P2264B_P2266_FULL_DATA_BACKTEST_PIPELINE_20260618_162142\edge_ranking\P2271_PAPER_SIMULATOR_OPEN_CHARTS_20260619_153314\logs\p2271_paper_simulator.log"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Add-Content $logFile $line -Encoding UTF8
    Write-Host $line
}

function New-SignalId($symbol, $strategy) {
    return "P2271_" + $symbol + "_" + $strategy + "_" + (Get-Date -Format "yyyyMMdd_HHmmss")
}

function Send-Signal($symbol, $action, $lot, $strategy) {
    if (Test-Path $orderFile) {
        Log "WAIT | MT5 ainda nao consumiu sinal anterior"
        return
    }

    $id = New-SignalId $symbol $strategy
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fff"
    $payload = "$symbol,$action,$lot,$id,$ts"

    Set-Content -Path $orderFile -Value $payload -Encoding ASCII -NoNewline
    Log "SIGNAL_SENT | $payload"
}

Log "P2271 PAPER SIMULATOR START"
Log "EDGES: $($edges.Count)"

$cycle = 0

while ($true) {
    foreach ($e in $edges) {
        $cycle++

        $symbol = $e.symbol
        $tf = $e.timeframe
        $strategy = $e.strategy
        $lot = "0.01"

        # Simulador simples: alterna BUY/SELL para validar execução visual.
        # Próximo passo: trocar por leitura dos candles + regra real do edge.
        if ($cycle % 2 -eq 0) { $action = "BUY" } else { $action = "SELL" }

        Send-Signal $symbol $action $lot $strategy

        Start-Sleep -Seconds 20
    }
}
