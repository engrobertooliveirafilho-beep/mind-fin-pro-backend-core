import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

INP=Path("reports/P16.23_EDGE_DECAY_REVALIDATION_AUTO_ARCHIVE/p1623_revalidated_edge_memory.json")
OUT=Path("reports/P16.24_ASSET_REGIME_EDGE_ALLOCATION")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load():
    return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []

def score(e):
    pf=float(e.get("profit_factor") or 0)
    trades=float(e.get("trades") or 0)
    dd=float(e.get("max_drawdown") or 0)
    decay=float(e.get("decay_revalidation_score") or 0)
    return round((min(pf,4)*0.45)+(min(trades,80)/80*1.5)+(max(0,1-dd)*0.75)+(1-decay)*1.25,6)

def allocate():
    by_asset=defaultdict(list)
    by_regime=defaultdict(list)
    for e in load():
        x={**e,"allocation_score":score(e),**BLOCKS}
        by_asset[x.get("asset") or x.get("symbol") or "UNKNOWN"].append(x)
        by_regime[x.get("regime") or "UNSPECIFIED"].append(x)
    return {
        "by_asset":{k:sorted(v,key=lambda x:x["allocation_score"],reverse=True) for k,v in by_asset.items()},
        "by_regime":{k:sorted(v,key=lambda x:x["allocation_score"],reverse=True) for k,v in by_regime.items()}
    }

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    a=allocate()
    total=sum(len(v) for v in a["by_asset"].values())
    report={
        "STATUS":"P16.24_ASSET_REGIME_EDGE_ALLOCATION_ENGINE_IMPLEMENTED",
        "INPUT_EDGES":total,
        "ASSETS":len(a["by_asset"]),
        "REGIMES":len(a["by_regime"]),
        "NEXT":"P16.25_PAPER_PORTFOLIO_CONSTRUCTION_FROM_ACTIVE_EDGES",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1624_allocation_by_asset.json").write_text(json.dumps(a["by_asset"],indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1624_allocation_by_regime.json").write_text(json.dumps(a["by_regime"],indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1624_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
