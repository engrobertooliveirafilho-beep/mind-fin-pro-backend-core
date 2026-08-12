import json
import time
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P1501_EDGE_EVOLUTION_LIVE_MONITOR")
OUT.mkdir(parents=True, exist_ok=True)

P1100 = Path("reports/P1100_1500X_AUTONOMOUS_EDGE_EVOLUTION_ECOSYSTEM/p1100_1500_master_report.json")
P203 = Path("reports/P203_400X_MASSIVE_RESEARCH_EVOLUTION_FACTORY/p203_400_master_report.json")
P401F = Path("reports/P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO/p401f_report.json")
P401G = Path("reports/P401G_TOP_EDGE_SELECTION_LOW_DD/p401g_report.json")
P501 = Path("reports/P501_600X_SHADOW_TO_DEMO_DECISION_GATE/p501_600_master_report.json")
P601 = Path("reports/P601_700X_INSTITUTIONAL_ALLOCATION_AND_CAPITAL_ENGINE/p601_700_master_report.json")

def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def snapshot():
    p1100 = load(P1100)
    p203 = load(P203)
    p401f = load(P401F)
    p401g = load(P401G)
    p501 = load(P501)
    p601 = load(P601)

    discovered = int(p1100.get("RESEARCH_INPUTS_DISCOVERED") or 0)
    generated = int(p1100.get("AUTO_STRATEGIES_GENERATED") or 0)
    backtested = int(p203.get("BACKTESTS_EXECUTED") or 0)
    candidates = int(p203.get("BACKTEST_CANDIDATES") or 0)
    wf = int(p401f.get("WALK_FORWARD_APPROVED") or 0)
    mc = int(p401f.get("MONTE_CARLO_APPROVED") or 0)
    promoted = int(p401f.get("PROMOTED_LOW_DD_EDGES") or p203.get("PROMOTED_EDGES") or 0)
    top100 = int(p401g.get("TOP100") or 0)
    top30 = int(p401g.get("TOP30") or 0)
    top10 = int(p401g.get("TOP10") or 0)
    demo_candidates = int(p501.get("CERTIFIED_DEMO_CANDIDATES") or 0)
    allocated = int(p601.get("ALLOCATED_EDGES") or 0)

    used_strategies = top10
    absorbed_today = discovered
    generated_today = generated
    backtested_today = backtested
    validated_today = mc
    promoted_today = promoted

    health = "GREEN"
    if backtested == 0 or generated == 0:
        health = "YELLOW"
    if discovered == 0 and generated == 0 and backtested == 0:
        health = "RED"

    return {
        "STATUS": "P1501_EDGE_EVOLUTION_LIVE_MONITOR_SNAPSHOT",
        "FLOW": "DISCOVER -> GENERATE -> BACKTEST -> VALIDATE -> PROMOTE",
        "DISCOVERED_RESEARCH_INPUTS": discovered,
        "WEB_STRATEGIES_ABSORBED_TODAY": absorbed_today,
        "AUTO_STRATEGIES_GENERATED_TODAY": generated_today,
        "STRATEGIES_USED_IN_SELECTION": used_strategies,
        "BACKTESTS_EXECUTED_TODAY": backtested_today,
        "BACKTEST_CANDIDATES": candidates,
        "WALK_FORWARD_APPROVED": wf,
        "MONTE_CARLO_APPROVED": mc,
        "EDGES_PROMOTED_TODAY": promoted_today,
        "TOP100": top100,
        "TOP30": top30,
        "TOP10": top10,
        "DEMO_CANDIDATES": demo_candidates,
        "ALLOCATED_EDGES": allocated,
        "HEALTH": health,
        "ORDER_SENT": False,
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN",
        "generated_at": datetime.now(UTC).isoformat()
    }

def print_snapshot(s):
    print("")
    print("====================================================")
    print(" MIND TRADER — EDGE EVOLUTION LIVE MONITOR")
    print("====================================================")
    print(f"STATUS: {s['STATUS']}")
    print(f"HEALTH: {s['HEALTH']}")
    print("")
    print("FLOW:")
    print("  DESCOBRIR  ->  GERAR  ->  BACKTESTAR  ->  VALIDAR  ->  PROMOVER")
    print("")
    print(f"DESCOBERTAS / WEB INPUTS:       {s['DISCOVERED_RESEARCH_INPUTS']}")
    print(f"ESTRATÉGIAS ABSORVIDAS HOJE:    {s['WEB_STRATEGIES_ABSORBED_TODAY']}")
    print(f"ESTRATÉGIAS GERADAS HOJE:       {s['AUTO_STRATEGIES_GENERATED_TODAY']}")
    print(f"ESTRATÉGIAS USADAS NA SELEÇÃO:  {s['STRATEGIES_USED_IN_SELECTION']}")
    print(f"BACKTESTS EXECUTADOS HOJE:      {s['BACKTESTS_EXECUTED_TODAY']}")
    print(f"CANDIDATOS BACKTEST:            {s['BACKTEST_CANDIDATES']}")
    print(f"WALK FORWARD APROVADOS:         {s['WALK_FORWARD_APPROVED']}")
    print(f"MONTE CARLO APROVADOS:          {s['MONTE_CARLO_APPROVED']}")
    print(f"EDGES PROMOVIDOS HOJE:          {s['EDGES_PROMOTED_TODAY']}")
    print("")
    print(f"TOP100:                         {s['TOP100']}")
    print(f"TOP30:                          {s['TOP30']}")
    print(f"TOP10:                          {s['TOP10']}")
    print(f"DEMO CANDIDATES:                {s['DEMO_CANDIDATES']}")
    print(f"ALLOCATED EDGES:                {s['ALLOCATED_EDGES']}")
    print("")
    print(f"REAL_ORDERS:                    {s['REAL_ORDERS']}")
    print(f"FTMO_REAL:                      {s['FTMO_REAL']}")
    print(f"MT5_REAL:                       {s['MT5_REAL']}")
    print("====================================================")
    print("")

def run_once():
    s = snapshot()
    (OUT / "latest_edge_evolution_monitor.json").write_text(
        json.dumps(s, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print_snapshot(s)

def run_loop(seconds=60, interval=10):
    end = time.time() + seconds
    while time.time() < end:
        run_once()
        time.sleep(interval)

if __name__ == "__main__":
    run_once()
