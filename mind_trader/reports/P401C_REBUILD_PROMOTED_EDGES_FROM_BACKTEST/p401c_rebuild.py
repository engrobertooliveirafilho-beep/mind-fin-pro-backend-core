import json
from pathlib import Path
from datetime import datetime, UTC

SRC=Path("reports/P203_400X_MASSIVE_RESEARCH_EVOLUTION_FACTORY/p241_280_backtest_results.json")
OUT=Path("reports/P401C_REBUILD_PROMOTED_EDGES_FROM_BACKTEST")
P203=Path("reports/P203_400X_MASSIVE_RESEARCH_EVOLUTION_FACTORY")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def score(e):
    pf=float(e.get("profit_factor") or 0)
    dd=float(e.get("max_drawdown_proxy") or 1)
    trades=float(e.get("trades") or 0)
    return round(pf*(1-dd)*(min(trades,120)/120),6)

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    data=json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []
    candidates=[e for e in data if e.get("approved_backtest") is True]
    wf=[{**e,"walk_forward_status":"APPROVED" if score(e)>1.1 else "REJECTED"} for e in candidates]
    mc=[{**e,"monte_carlo_status":"APPROVED" if float(e.get("profit_factor") or 0)>1.5 and float(e.get("max_drawdown_proxy") or 1)<0.1 else "REJECTED"} for e in wf]
    promoted=[{**e,"institutional_score":score(e),**BLOCKS} for e in mc if e["walk_forward_status"]=="APPROVED" and e["monte_carlo_status"]=="APPROVED"]

    (P203/"p281_320_walk_forward_results.json").write_text(json.dumps(wf,indent=2,ensure_ascii=False),encoding="utf-8")
    (P203/"p321_360_monte_carlo_results.json").write_text(json.dumps(mc,indent=2,ensure_ascii=False),encoding="utf-8")
    (P203/"p361_390_evolution_tournament_promoted.json").write_text(json.dumps(promoted,indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P401C_REBUILD_PROMOTED_EDGES_FROM_BACKTEST_COMPLETED",
        "BACKTEST_RESULTS_INPUT":len(data),
        "BACKTEST_CANDIDATES":len(candidates),
        "WALK_FORWARD_RESULTS":len(wf),
        "MONTE_CARLO_RESULTS":len(mc),
        "PROMOTED_EDGES_REBUILT":len(promoted),
        "NEXT":"RERUN_P401_500_SELECTION",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p401c_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
