import json
from pathlib import Path
from datetime import datetime, UTC

SRC=Path("reports/P401H_TIMEFRAME_DIVERSIFICATION_FIX/p401h_top10_timeframe_balanced.json")
POS=Path("reports/P79_DEMO_ORDER_AUDIT_POSITION_MONITOR/p79_positions.json")
OUT=Path("reports/P402_LOW_DD_DEMO_SHADOW_ROUTING")

BLOCKS={"LIVE":"FORBIDDEN","REAL_BROKER":"DISABLED","REAL_ORDERS":"FORBIDDEN","FTMO_REAL":"FORBIDDEN","MT5_REAL":"FORBIDDEN"}

def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []

def run():
    OUT.mkdir(parents=True,exist_ok=True)

    edges=load(SRC)
    positions=load(POS)

    active_symbols=set(p.get("symbol") for p in positions)

    routes=[]
    for i,e in enumerate(edges):
        asset=e.get("asset")
        tf=e.get("timeframe") or e.get("target_timeframe")
        score=float(e.get("institutional_score") or 0)

        action="SHADOW_WATCH"
        reason="NO_EXECUTION_SHADOW_MODE"

        if asset in active_symbols:
            action="SHADOW_MONITOR_EXISTING_POSITION"
            reason="ASSET_ALREADY_OPEN"

        routes.append({
            "rank":i+1,
            "edge_id":e.get("job_id"),
            "asset":asset,
            "timeframe":tf,
            "family":e.get("family"),
            "score":score,
            "shadow_action":action,
            "reason":reason,
            "order_sent":False,
            **BLOCKS
        })

    report={
        "STATUS":"P402_LOW_DD_DEMO_SHADOW_ROUTING_COMPLETED",
        "INPUT_TOP10_EDGES":len(edges),
        "POSITIONS_INPUT":len(positions),
        "SHADOW_ROUTES":len(routes),
        "ORDER_SENT":False,
        "POSITION_CLOSE_SENT":False,
        "TOP_ROUTE":routes[0] if routes else None,
        "NEXT":"P403_SHADOW_SIGNAL_SCORING_AND_JOURNALING",
        **BLOCKS,
        "generated_at":datetime.now(UTC).isoformat()
    }

    (OUT/"p402_shadow_routes.json").write_text(json.dumps(routes,indent=2,ensure_ascii=False),encoding="utf-8")
    (OUT/"p402_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
