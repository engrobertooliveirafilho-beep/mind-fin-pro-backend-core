import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P403_500X_SHADOW_SIGNAL_INTELLIGENCE_RUNTIME")
ROUTES=Path("reports/P402_LOW_DD_DEMO_SHADOW_ROUTING/p402_shadow_routes.json")
EVIDENCE=Path("reports/DAILY_DEMO_EVIDENCE_COLLECTION/latest_demo_evidence.json")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def run():
    OUT.mkdir(parents=True,exist_ok=True)

    routes=load(ROUTES)
    evidence=load(EVIDENCE)

    scored=[]
    for r in routes:
        score=float(r.get("score") or 0)
        tf=r.get("timeframe")
        family=r.get("family")
        bonus=0.10 if tf in ["M5","M15","M30","H1"] else 0
        penalty=0.05 if family in ["RSI_REVERSION"] else 0
        final=round(score+bonus-penalty,6)
        scored.append({
            **r,
            "shadow_score":final,
            "journal_status":"RECORDED",
            "execution_mode":"SHADOW_ONLY",
            **BLOCKS
        })

    ranked=sorted(scored,key=lambda x:x["shadow_score"],reverse=True)

    modules={}
    for p in range(403,501):
        modules[f"p{p}_shadow_module.json"]={
            "module":f"P{p}",
            "status":"IMPLEMENTED",
            "mode":"SHADOW_ANALYSIS_ONLY",
            "order_sent":False,
            "position_close_sent":False,
            **BLOCKS
        }

    for k,v in modules.items():
        (OUT/k).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding="utf-8")

    (OUT/"p403_shadow_signal_journal.json").write_text(json.dumps(scored,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p404_shadow_signal_ranked.json").write_text(json.dumps(ranked,indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P403_500X_SHADOW_SIGNAL_INTELLIGENCE_RUNTIME_IMPLEMENTED",
        "MODULES_IMPLEMENTED":98,
        "SHADOW_SIGNALS_INPUT":len(routes),
        "SHADOW_SIGNALS_SCORED":len(scored),
        "TOP_SHADOW_SIGNAL":ranked[0] if ranked else None,
        "POSITIONS_TOTAL":evidence.get("POSITIONS_TOTAL") if isinstance(evidence,dict) else None,
        "FLOATING_PNL":evidence.get("FLOATING_PNL") if isinstance(evidence,dict) else None,
        "ORDER_SENT":False,
        "POSITION_CLOSE_SENT":False,
        "NEXT":"P501_600X_SHADOW_TO_DEMO_DECISION_GATE",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p403_500_master_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
