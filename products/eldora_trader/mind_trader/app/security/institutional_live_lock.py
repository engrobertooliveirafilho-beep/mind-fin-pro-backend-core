import json
from pathlib import Path
from datetime import datetime, UTC

FORBIDDEN_ACTIONS = {
    "LIVE_TRADE",
    "PRODUCTION_TRADE",
    "REAL_MONEY_TRADE",
    "FTMO_REAL_TRADE",
    "BROKER_SEND_ORDER",
    "ENABLE_LIVE_ROUTING",
    "PRODUCTION_APPROVAL"
}

def institutional_live_lock(action, payload=None):
    payload=payload or {}
    blocked=action in FORBIDDEN_ACTIONS
    report={
        "lock":"P8.92_INSTITUTIONAL_LIVE_LOCK",
        "created_at":datetime.now(UTC).isoformat(),
        "action":action,
        "payload":payload,
        "blocked":blocked,
        "decision":"FORCE_BLOCK_LIVE_OR_PRODUCTION" if blocked else "ALLOW_NON_LIVE_RESEARCH_ACTION",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    Path("mind_trader/reports").mkdir(parents=True,exist_ok=True)
    Path("mind_trader/reports/P8.92_institutional_live_lock.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

def assert_not_live_action(action):
    r=institutional_live_lock(action)
    if r["blocked"]:
        return False, r["decision"]
    return True, r["decision"]
