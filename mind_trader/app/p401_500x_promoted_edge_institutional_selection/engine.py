import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

OUT=Path("reports/P401_500X_PROMOTED_EDGE_INSTITUTIONAL_SELECTION")
SRC=Path("reports/P203_400X_MASSIVE_RESEARCH_EVOLUTION_FACTORY/p361_390_evolution_tournament_promoted.json")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def load():
    return json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []

def institutional_score(e):
    pf=float(e.get("profit_factor") or 1)
    dd=float(e.get("max_drawdown_proxy") or 0.2)
    trades=float(e.get("trades") or 1)
    return round((pf*(1-dd))*(min(trades,120)/120),6)

def diversified_select(edges, limit):
    selected=[]
    buckets=defaultdict(int)
    ranked=sorted(edges,key=institutional_score,reverse=True)
    for e in ranked:
        key=(e.get("asset"),e.get("target_timeframe"),e.get("family"))
        if buckets[key] >= 3:
            continue
        selected.append({**e,"institutional_score":institutional_score(e),**BLOCKS})
        buckets[key]+=1
        if len(selected)>=limit:
            break
    return selected

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    edges=load()

    top300=diversified_select(edges,300)
    top100=diversified_select(top300,100)
    top30=diversified_select(top100,30)
    top10=diversified_select(top30,10)

    artifacts={
        "p401_430_top300_operational_arsenal.json":top300,
        "p431_460_top100_institutional_edges.json":top100,
        "p461_480_top30_ftmo_watchlist.json":top30,
        "p481_500_top10_execution_candidates.json":top10
    }

    for k,v in artifacts.items():
        (OUT/k).write_text(json.dumps(v,indent=2,ensure_ascii=False,default=str),encoding="utf-8")

    assets=len(set(e.get("asset") for e in top100))
    tfs=len(set(e.get("target_timeframe") for e in top100))
    fams=len(set(e.get("family") for e in top100))

    report={
        "STATUS":"P401_500X_PROMOTED_EDGE_INSTITUTIONAL_SELECTION_IMPLEMENTED",
        "INPUT_PROMOTED_EDGES":len(edges),
        "TOP300":len(top300),
        "TOP100":len(top100),
        "TOP30":len(top30),
        "TOP10":len(top10),
        "TOP100_ASSETS":assets,
        "TOP100_TIMEFRAMES":tfs,
        "TOP100_FAMILIES":fams,
        "DAY_TRADER_EDGES":len([e for e in top100 if e.get("target_timeframe") in ["M1","M2","M5","M15","M30"]]),
        "SWING_TRADER_EDGES":len([e for e in top100 if e.get("target_timeframe") in ["H1","H4","D1","W1","MN1"]]),
        "NEXT":"P501_600X_DEMO_EXECUTION_SELECTION_AND_SHADOW_ROUTING",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p401_500_master_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
