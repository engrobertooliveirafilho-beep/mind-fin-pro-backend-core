import json
from pathlib import Path
from datetime import datetime, UTC

INP=Path("reports/P16.21M_VIDEO_EDGE_MEMORY_MERGE/p1621m_merged_edge_memory.json")
OUT=Path("reports/P16.23_EDGE_DECAY_REVALIDATION_AUTO_ARCHIVE")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","CAUSALITY":"NOT_PROVEN"}

def load():
    return json.loads(INP.read_text(encoding="utf-8")) if INP.exists() else []

def decay_score(e):
    pf=float(e.get("profit_factor") or 0)
    trades=float(e.get("trades") or 0)
    dd=float(e.get("max_drawdown") or 0)
    mc=float(e.get("monte_carlo_stability") or 1)
    score=max(0, min(1, 1 - ((min(pf,4)/4)*0.45 + (min(trades,80)/80)*0.20 + (min(mc,3)/3)*0.25 + (1-min(dd,0.5))*0.10)))
    return round(score,6)

def classify(e):
    d=decay_score(e)
    if d>=0.55:
        status="ARCHIVED_DECAY"
    elif d>=0.35:
        status="WATCHLIST_DECAY"
    else:
        status="ACTIVE_EDGE"
    return {**e,"decay_revalidation_score":d,"memory_status":status,"revalidated_at":datetime.now(UTC).isoformat(),**BLOCKS}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    edges=[classify(e) for e in load()]
    active=[e for e in edges if e["memory_status"]=="ACTIVE_EDGE"]
    watch=[e for e in edges if e["memory_status"]=="WATCHLIST_DECAY"]
    archived=[e for e in edges if e["memory_status"]=="ARCHIVED_DECAY"]
    report={
        "STATUS":"P16.23_EDGE_DECAY_REVALIDATION_AND_AUTO_ARCHIVE_IMPLEMENTED",
        "INPUT_EDGES":len(edges),
        "ACTIVE_EDGES":len(active),
        "WATCHLIST_EDGES":len(watch),
        "ARCHIVED_EDGES":len(archived),
        "NEXT":"P16.24_ASSET_REGIME_EDGE_ALLOCATION_ENGINE",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (OUT/"p1623_revalidated_edge_memory.json").write_text(json.dumps(edges,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1623_active_edges.json").write_text(json.dumps(active,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1623_watchlist_edges.json").write_text(json.dumps(watch,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1623_archived_edges.json").write_text(json.dumps(archived,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p1623_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
