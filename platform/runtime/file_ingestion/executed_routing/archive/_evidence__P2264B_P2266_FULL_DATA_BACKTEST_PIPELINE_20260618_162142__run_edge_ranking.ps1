$ErrorActionPreference = "Stop"

$OUT = "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\_evidence\P2264B_P2266_FULL_DATA_BACKTEST_PIPELINE_20260618_162142"
$results = Join-Path $OUT "edge_ranking\p2265_results.csv"

@'
symbol,timeframe,strategy,params,pf,winrate,trades,maxdd,payoff,netprofit,status
PENDING,PENDING,PENDING,PENDING,,,,,,,WAITING_REAL_BACKTEST_ENGINE
'@ | Set-Content $results -Encoding UTF8

Write-Host "[OK] Ranking placeholder criado:" $results
Write-Host "Próximo passo: conectar backtest engine real para preencher métricas."
