from datetime import datetime, timezone

AUDIT_EVENTS = []

def audit_event(event_type: str, actor: str = "system", payload: dict | None = None):
    event = {
        "event_type": event_type,
        "actor": actor,
        "payload": payload or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    AUDIT_EVENTS.append(event)
    return event

def audit_report():
    return {"status": "ok", "events_count": len(AUDIT_EVENTS), "events": AUDIT_EVENTS[-20:]}
