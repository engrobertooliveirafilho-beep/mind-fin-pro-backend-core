import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

SRC=Path("reports/P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO/p401f_promoted_low_dd_edges.json")
OUT=Path("reports/P401G_TOP_EDGE_SELECTION_LOW_DD")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def score(e):
    return float(e.get("institutional_score") or 0)

def diversified_select(edges, limit, max_per_bucket=3):
    selected=[]
    buckets=defaultdict(int)
    ranked=sorted(edges,key=score,reverse=True)

    for e in ranked:
        bucket=(e.get("asset"),e.get("timeframe"),e.get("family"))
        if buckets[bucket] >= max_per_bucket:
            continue
        selected.append({**e,"selection_rank":len(selected)+1,**BLOCKS})
        buckets[bucket]+=1
        if len(selected)>=limit:
            break

    return selected

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    edges=json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []

    top100=diversified_select(edges,100,3)
    top30=diversified_select(edges,30,2)
    top10=diversified_select(edges,10,1)

    (OUT/"p401g_top100_low_dd_edges.json").write_text(json.dumps(top100,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p401g_top30_low_dd_edges.json").write_text(json.dumps(top30,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p401g_top10_low_dd_edges.json").write_text(json.dumps(top10,indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P401G_TOP_EDGE_SELECTION_LOW_DD_COMPLETED",
        "INPUT_PROMOTED_LOW_DD_EDGES":len(edges),
        "TOP100":len(top100),
        "TOP30":len(top30),
        "TOP10":len(top10),
        "TOP100_ASSETS":len(set(e.get("asset") for e in top100)),
        "TOP100_TIMEFRAMES":len(set(e.get("timeframe") for e in top100)),
        "TOP100_FAMILIES":len(set(e.get("family") for e in top100)),
        "TOP10_ASSETS":len(set(e.get("asset") for e in top10)),
        "TOP10_TIMEFRAMES":len(set(e.get("timeframe") for e in top10)),
        "TOP10_FAMILIES":len(set(e.get("family") for e in top10)),
        "NEXT":"P402_LOW_DD_DEMO_SHADOW_ROUTING",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p401g_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
