import json, statistics
from pathlib import Path
from datetime import datetime, UTC

SRC=Path("reports/P401E_LOW_DRAWDOWN_STRATEGY_RESEARCH/p401e_low_dd_results.json")
OUT=Path("reports/P401E2_LOW_DD_OUTLIER_AND_OVERFIT_FILTER")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    data=json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []

    filtered=[]
    rejected=[]

    for e in data:
        pf=float(e.get("profit_factor") or 0)
        dd=float(e.get("max_drawdown") or 0)
        trades=int(e.get("trades") or 0)

        reasons=[]

        if trades < 50:
            reasons.append("LOW_TRADES")
        if pf <= 1.05:
            reasons.append("LOW_PF")
        if pf > 10:
            reasons.append("PF_OUTLIER")
        if dd <= 0.0001:
            reasons.append("DD_ZERO_OR_ARTIFICIAL")
        if dd > 0.08:
            reasons.append("DD_TOO_HIGH")

        if reasons:
            rejected.append({**e,"reject_reasons":reasons,**BLOCKS})
        else:
            score=round(pf*(1-dd)*(min(trades,200)/200),6)
            filtered.append({**e,"institutional_score":score,"overfit_filter":"PASS",**BLOCKS})

    filtered=sorted(filtered,key=lambda x:x["institutional_score"],reverse=True)

    (OUT/"p401e2_filtered_candidates.json").write_text(json.dumps(filtered,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p401e2_rejected_candidates.json").write_text(json.dumps(rejected[:1000],indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P401E2_LOW_DD_OUTLIER_AND_OVERFIT_FILTER_COMPLETED",
        "INPUT_RESULTS":len(data),
        "FILTERED_CANDIDATES":len(filtered),
        "REJECTED":len(rejected),
        "TOP_SCORE":filtered[0]["institutional_score"] if filtered else None,
        "TOP_PF":filtered[0]["profit_factor"] if filtered else None,
        "TOP_DD":filtered[0]["max_drawdown"] if filtered else None,
        "NEXT":"P401F_LOW_DD_WALK_FORWARD_MONTE_CARLO" if filtered else "EXPAND_LOW_DD_RESEARCH",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p401e2_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
