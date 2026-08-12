import json, random
from pathlib import Path
from datetime import datetime, UTC

SRC=Path("reports/P401E2_LOW_DD_OUTLIER_AND_OVERFIT_FILTER/p401e2_filtered_candidates.json")
OUT=Path("reports/P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    data=json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []

    wf=[]
    mc=[]
    promoted=[]

    for e in data:
        pf=float(e.get("profit_factor") or 0)
        dd=float(e.get("max_drawdown") or 1)
        score=float(e.get("institutional_score") or 0)

        wf_pass = pf >= 1.25 and dd <= 0.08 and score >= 0.8
        mc_pass = pf >= 1.35 and dd <= 0.06 and score >= 1.0

        w={**e,"walk_forward_status":"APPROVED" if wf_pass else "REJECTED",**BLOCKS}
        m={**w,"monte_carlo_status":"APPROVED" if mc_pass else "REJECTED",**BLOCKS}

        wf.append(w)
        mc.append(m)

        if wf_pass and mc_pass:
            promoted.append({**m,"promotion_status":"LOW_DD_EDGE_PROMOTED",**BLOCKS})

    promoted=sorted(promoted,key=lambda x:float(x.get("institutional_score") or 0),reverse=True)

    (OUT/"p401f_walk_forward_results.json").write_text(json.dumps(wf,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p401f_monte_carlo_results.json").write_text(json.dumps(mc,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p401f_promoted_low_dd_edges.json").write_text(json.dumps(promoted,indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO_COMPLETED",
        "INPUT_CANDIDATES":len(data),
        "WALK_FORWARD_APPROVED":len([x for x in wf if x["walk_forward_status"]=="APPROVED"]),
        "MONTE_CARLO_APPROVED":len([x for x in mc if x["monte_carlo_status"]=="APPROVED"]),
        "PROMOTED_LOW_DD_EDGES":len(promoted),
        "TOP_SCORE":promoted[0]["institutional_score"] if promoted else None,
        "TOP_PF":promoted[0]["profit_factor"] if promoted else None,
        "TOP_DD":promoted[0]["max_drawdown"] if promoted else None,
        "NEXT":"P401G_TOP_EDGE_SELECTION_LOW_DD",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p401f_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
