from datetime import datetime, timezone

SELF_HEALING_STATE = {
    "recoveries": [],
    "runtime_status": "healthy"
}

def trigger_recovery(component: str = "runtime"):
    recovery = {
        "component": component,
        "status": "recovered",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    SELF_HEALING_STATE["recoveries"].append(recovery)

    return {
        "status": "ok",
        "recovery": recovery,
        "recoveries_total": len(SELF_HEALING_STATE["recoveries"])
    }

def healing_report():
    return {
        "status": "ok",
        "runtime_status": SELF_HEALING_STATE["runtime_status"],
        "recoveries_total": len(SELF_HEALING_STATE["recoveries"]),
        "recoveries": SELF_HEALING_STATE["recoveries"][-20:]
    }
