$ErrorActionPreference="Continue";

Set-Location "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\mind_trader"

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "reports\P1000_AUTONOMOUS_DAILY_SCHEDULER\logs"
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = "$logDir\daily_run_$stamp.log"

function Run-Step($name, $cmd) {
    "`n=== $name ===" | Tee-Object -FilePath $log -Append
    Invoke-Expression $cmd 2>&1 | Tee-Object -FilePath $log -Append
}

Run-Step "DAILY_DEMO_EVIDENCE_COLLECTION" "python reports\DAILY_DEMO_EVIDENCE_COLLECTION\collect_daily_demo_evidence.py"
Run-Step "P201_DAILY_DEMO_EVIDENCE_ANALYZER" "python -c `"from app.p201_daily_demo_evidence_analyzer.engine import run; import json; print(json.dumps(run(),indent=2,ensure_ascii=False))`""
Run-Step "P202_DEMO_TRADE_JOURNAL_ENGINE" "python -c `"from app.p202_demo_trade_journal_engine.engine import run; import json; print(json.dumps(run(),indent=2,ensure_ascii=False))`""

Run-Step "P203_400_MASSIVE_RESEARCH_EVOLUTION" "python -c `"from app.p203_400x_massive_research_evolution_factory.engine import run; import json; print(json.dumps(run(max_jobs=50000),indent=2,ensure_ascii=False))`""

Run-Step "P401E_LOW_DD_RESEARCH" "python reports\P401E_LOW_DRAWDOWN_STRATEGY_RESEARCH\p401e_low_dd.py"
Run-Step "P401E2_OVERFIT_FILTER" "python reports\P401E2_LOW_DD_OUTLIER_AND_OVERFIT_FILTER\p401e2_filter.py"
Run-Step "P401F_WF_MC" "python reports\P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO\p401f_wf_mc.py"
Run-Step "P401G_TOP_SELECTION" "python reports\P401G_TOP_EDGE_SELECTION_LOW_DD\p401g_select.py"
Run-Step "P401H_TIMEFRAME_FIX" "python reports\P401H_TIMEFRAME_DIVERSIFICATION_FIX\p401h_fix.py"
Run-Step "P402_SHADOW_ROUTING" "python reports\P402_LOW_DD_DEMO_SHADOW_ROUTING\p402_shadow_routing.py"
Run-Step "P403_500_SHADOW_INTELLIGENCE" "python reports\P403_500X_SHADOW_SIGNAL_INTELLIGENCE_RUNTIME\p403_500_runtime.py"
Run-Step "P501_600_DECISION_GATE" "python reports\P501_600X_SHADOW_TO_DEMO_DECISION_GATE\p501_600_runtime.py"
Run-Step "P601_700_ALLOCATION" "python reports\P601_700X_INSTITUTIONAL_ALLOCATION_AND_CAPITAL_ENGINE\p601_700_runtime.py"

@{
STATUS="P1000_DAILY_AUTONOMOUS_RUN_COMPLETED"
TIMESTAMP=$stamp
LOG=$log
ORDER_SEND_ALLOWED=$false
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
MT5_REAL="FORBIDDEN"
} | ConvertTo-Json -Depth 10 |
Set-Content reports\P1000_AUTONOMOUS_DAILY_SCHEDULER\latest_daily_run.json
