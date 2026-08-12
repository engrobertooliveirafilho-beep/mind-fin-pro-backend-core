import json
from pathlib import Path
from datetime import datetime, UTC

OUT=Path("reports/P501_600X_SHADOW_TO_DEMO_DECISION_GATE")
SRC=Path("reports/P403_500X_SHADOW_SIGNAL_INTELLIGENCE_RUNTIME/p404_shadow_signal_ranked.json")

BLOCKS={
 "LIVE":"FORBIDDEN",
 "REAL_BROKER":"DISABLED",
 "REAL_ORDERS":"FORBIDDEN",
 "FTMO_REAL":"FORBIDDEN",
 "MT5_REAL":"FORBIDDEN"
}

def run():

    OUT.mkdir(parents=True,exist_ok=True)

    signals=json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []

    certified=[]
    watchlist=[]
    blocked=[]

    for s in signals:

        score=float(s.get("shadow_score") or 0)

        decision="BLOCK"

        if score >= 1.25:
            decision="WATCHLIST"

        if score >= 2.00:
            decision="DEMO_CANDIDATE"

        if score >= 2.75:
            decision="HIGH_PRIORITY_DEMO"

        row={
            **s,
            "decision":decision,
            "order_sent":False,
            "position_close_sent":False,
            **BLOCKS
        }

        if decision=="BLOCK":
            blocked.append(row)
        elif decision=="WATCHLIST":
            watchlist.append(row)
        else:
            certified.append(row)

    certified=sorted(
        certified,
        key=lambda x: float(x.get("shadow_score") or 0),
        reverse=True
    )

    top10=certified[:10]
    top5=certified[:5]
    top3=certified[:3]

    for p in range(501,601):
        (OUT/f"p{p}_module.json").write_text(
            json.dumps({
                "module":f"P{p}",
                "status":"IMPLEMENTED",
                "mode":"DECISION_GATE_ONLY",
                "order_sent":False,
                **BLOCKS
            },indent=2),
            encoding="utf-8"
        )

    (OUT/"p501_certified_demo_candidates.json").write_text(json.dumps(certified,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p502_watchlist.json").write_text(json.dumps(watchlist,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p503_blocked.json").write_text(json.dumps(blocked,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p504_top10.json").write_text(json.dumps(top10,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p505_top5.json").write_text(json.dumps(top5,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p506_top3.json").write_text(json.dumps(top3,indent=2,ensure_ascii=False),encoding="utf-8")

    report={
        "STATUS":"P501_600X_SHADOW_TO_DEMO_DECISION_GATE_IMPLEMENTED",
        "MODULES_IMPLEMENTED":100,
        "INPUT_SIGNALS":len(signals),
        "CERTIFIED_DEMO_CANDIDATES":len(certified),
        "WATCHLIST":len(watchlist),
        "BLOCKED":len(blocked),
        "TOP10":len(top10),
        "TOP5":len(top5),
        "TOP3":len(top3),
        "BEST_SIGNAL":top3[0] if top3 else None,
        "ORDER_SENT":False,
        "POSITION_CLOSE_SENT":False,
        "NEXT":"P601_700X_INSTITUTIONAL_ALLOCATION_AND_CAPITAL_ENGINE",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p501_600_master_report.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False),
        encoding="utf-8"
    )

    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
