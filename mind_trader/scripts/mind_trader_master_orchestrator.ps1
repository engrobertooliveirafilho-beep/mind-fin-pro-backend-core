$ErrorActionPreference="Continue";

Set-Location "C:\Users\MindFin\Desktop\mind-fin-pro-backend-core\mind_trader"

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = "reports\P1001_AUTONOMOUS_MASTER_ORCHESTRATOR\logs"
New-Item -ItemType Directory -Force $logDir | Out-Null
$log = "$logDir\master_run_$stamp.log"

function Run-Step($name, $cmd) {
    "`n=== $name ===" | Tee-Object -FilePath $log -Append
    Invoke-Expression $cmd 2>&1 | Tee-Object -FilePath $log -Append
}

Run-Step "P1000_DAILY_AUTONOMOUS_PIPELINE" "powershell -ExecutionPolicy Bypass -File scripts\mind_trader_daily_autonomous.ps1"

Run-Step "P701_800_SUPERVISOR" "python reports\P701_800X_AUTONOMOUS_DEMO_OPERATING_SUPERVISOR\p701_800_runtime.py"

Run-Step "P801B_SUPERVISED_EDGE_LINK_FIX" '
New-Item -ItemType Directory -Force reports\P801B_SUPERVISED_EDGE_LINK_FIX,reports\P701_800X_AUTONOMOUS_DEMO_OPERATING_SUPERVISOR | Out-Null
$allocPath = "reports\P601_700X_INSTITUTIONAL_ALLOCATION_AND_CAPITAL_ENGINE\p601_700_allocation.json"
$superPath = "reports\P701_800X_AUTONOMOUS_DEMO_OPERATING_SUPERVISOR\p701_supervised_edges.json"
$outPath = "reports\P801B_SUPERVISED_EDGE_LINK_FIX\p801b_report.json"
$alloc = Get-Content $allocPath -Raw | ConvertFrom-Json -AsHashTable
$supervised = @(
foreach($a in $alloc){
$risk = 0.0
if($a.ContainsKey("risk_pct") -and $null -ne $a["risk_pct"]){ $risk = [double]$a["risk_pct"] }
if($risk -gt 0){
@{
edge_id=$a["edge_id"]; asset=$a["asset"]; timeframe=$a["timeframe"]; family=$a["family"];
risk_pct=$risk; risk_value=$a["risk_value"]; supervisor_status="ACTIVE"; health="GREEN";
execution_allowed=$false; shadow_only=$true;
LIVE="FORBIDDEN"; REAL_BROKER="DISABLED"; REAL_ORDERS="FORBIDDEN"; FTMO_REAL="FORBIDDEN"; MT5_REAL="FORBIDDEN"
}
}
}
)
$supervised | ConvertTo-Json -Depth 20 | Set-Content $superPath -Encoding UTF8
@{
STATUS="P801B_SUPERVISED_EDGE_LINK_FIX_COMPLETED"; ALLOC_INPUT=$alloc.Count; SUPERVISED_EDGES=$supervised.Count;
TARGET_FILE=$superPath; NEXT="RERUN_P801_1000_CERTIFICATION";
LIVE="FORBIDDEN"; REAL_BROKER="DISABLED"; REAL_ORDERS="FORBIDDEN"; FTMO_REAL="FORBIDDEN"; MT5_REAL="FORBIDDEN"
} | ConvertTo-Json -Depth 20 | Set-Content $outPath -Encoding UTF8
Get-Content $outPath
'

Run-Step "P801_1000_CERTIFICATION" "python reports\P801_1000X_INSTITUTIONAL_CERTIFICATION_RELEASE_AUTHORITY\p801_1000_runtime.py"

Run-Step "P1002_HEALTH" "python reports\P1002_RUNTIME_HEALTH_MONITOR\p1002_health.py"
Run-Step "P1003_RECOVERY" "python reports\P1003_AUTOMATIC_RECOVERY_ENGINE\p1003_recovery.py"
Run-Step "P1004_EXECUTIVE" "python reports\executive\p1004_daily_executive_report.py"

$latestEvidence = Get-Content reports\DAILY_DEMO_EVIDENCE_COLLECTION\latest_demo_evidence.json -Raw | ConvertFrom-Json
$p601 = Get-Content reports\P601_700X_INSTITUTIONAL_ALLOCATION_AND_CAPITAL_ENGINE\p601_700_master_report.json -Raw | ConvertFrom-Json
$p801 = Get-Content reports\P801_1000X_INSTITUTIONAL_CERTIFICATION_RELEASE_AUTHORITY\p801_1000_master_report.json -Raw | ConvertFrom-Json
$health = Get-Content reports\P1002_RUNTIME_HEALTH_MONITOR\p1002_health_report.json -Raw | ConvertFrom-Json
$recovery = Get-Content reports\P1003_AUTOMATIC_RECOVERY_ENGINE\p1003_recovery_report.json -Raw | ConvertFrom-Json

@{
STATUS="P1001_AUTONOMOUS_MASTER_ORCHESTRATOR_COMPLETED"
TIMESTAMP=$stamp
LOG=$log
EQUITY=$latestEvidence.EQUITY
FLOATING_PNL=$latestEvidence.FLOATING_PNL
POSITIONS_TOTAL=$latestEvidence.POSITIONS_TOTAL
ALLOCATED_EDGES=$p601.ALLOCATED_EDGES
SUPERVISED_EDGES=$p801.SUPERVISED_EDGES
CERTIFICATION=$p801.CERTIFICATION
FTMO_RELEASE=$p801.FTMO_RELEASE
HEALTH=$health.HEALTH
RECOVERY_REQUIRED=$recovery.RECOVERY_REQUIRED
ORDER_SEND_ALLOWED=$false
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"
MT5_REAL="FORBIDDEN"
} | ConvertTo-Json -Depth 10 |
Set-Content reports\P1001_AUTONOMOUS_MASTER_ORCHESTRATOR\master_daily_report.json

Get-Content reports\P1001_AUTONOMOUS_MASTER_ORCHESTRATOR\master_daily_report.json


Run-Step "P1100_1500_EDGE_EVOLUTION_ECOSYSTEM" "python reports\P1100_1500X_AUTONOMOUS_EDGE_EVOLUTION_ECOSYSTEM\p1100_1500_runtime.py"



Run-Step "P1501_EDGE_EVOLUTION_LIVE_MONITOR" "python reports\P1501_EDGE_EVOLUTION_LIVE_MONITOR\p1501_live_monitor.py"
Run-Step "P1502_DELTA_DAILY_EVOLUTION_MONITOR" "python reports\P1502_DELTA_DAILY_EVOLUTION_MONITOR\p1502_delta_monitor.py"



Run-Step "P1606_SCALING_DECISION_MONITOR" "python reports\P1606_CONFLUENCE_GATE_AND_SCALING_DECISION_MONITOR\p1606_scaling_decision_monitor.py"
Run-Step "P1607_WRITE_SCALING_STATE" "python reports\P1607_SCALING_STATE\p1607_write_scaling_state.py"



Run-Step "P1606_SCALING_DECISION_MONITOR" "python reports\P1606_CONFLUENCE_GATE_AND_SCALING_DECISION_MONITOR\p1606_scaling_decision_monitor.py"
Run-Step "P1607_WRITE_SCALING_STATE" "python reports\P1607_SCALING_STATE\p1607_write_scaling_state.py"

