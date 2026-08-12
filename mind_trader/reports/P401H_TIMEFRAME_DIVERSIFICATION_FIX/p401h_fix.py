import json
from pathlib import Path
from datetime import datetime, UTC
from collections import defaultdict

SRC=Path("reports/P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO/p401f_promoted_low_dd_edges.json")
OUT=Path("reports/P401H_TIMEFRAME_DIVERSIFICATION_FIX")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

TARGET_TFS=["M5","M15","M30","H1","H4","D1"]

def score(e):
    return float(e.get("institutional_score") or 0)

def select_timeframe_balanced(edges, limit):
    selected=[]
    used=set()
    ranked=sorted(edges,key=score,reverse=True)

    for tf in TARGET_TFS:
        bucket=[e for e in ranked if e.get("timeframe")==tf or e.get("target_timeframe")==tf]
        if bucket:
            e=bucket[0]
            selected.append({**e,"selection_rank":len(selected)+1,"selection_reason":"TIMEFRAME_REQUIRED",**BLOCKS})
            used.add(e.get("job_id"))

    for e in ranked:
        if len(selected)>=limit:
            break
        if e.get("job_id") in used:
            continue
        selected.append({**e,"selection_rank":len(selected)+1,"selection_reason":"SCORE_FILL",**BLOCKS})
        used.add(e.get("job_id"))

    return selected[:limit]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    edges=json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []

    top30=select_timeframe_balanced(edges,30)
    top10=select_timeframe_balanced(edges,10)

    (OUT/"p401h_top30_timeframe_balanced.json").write_text(json.dumps(top30,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p401h_top10_timeframe_balanced.json").write_text(json.dumps(top10,indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P401H_TIMEFRAME_DIVERSIFICATION_FIX_COMPLETED",
        "INPUT_EDGES":len(edges),
        "TOP30":len(top30),
        "TOP10":len(top10),
        "TOP30_TIMEFRAMES":len(set((e.get("timeframe") or e.get("target_timeframe")) for e in top30)),
        "TOP10_TIMEFRAMES":len(set((e.get("timeframe") or e.get("target_timeframe")) for e in top10)),
        "TOP10_ASSETS":len(set(e.get("asset") for e in top10)),
        "TOP10_FAMILIES":len(set(e.get("family") for e in top10)),
        "NEXT":"P402_LOW_DD_DEMO_SHADOW_ROUTING",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p401h_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
