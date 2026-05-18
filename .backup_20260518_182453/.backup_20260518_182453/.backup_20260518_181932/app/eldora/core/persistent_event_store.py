import os, json
from datetime import datetime, timezone

try:
    import psycopg2
except Exception:
    psycopg2 = None

MEMORY_AUDIT_EVENTS = []
MEMORY_EVENT_STORE = []

def _conn():
    url = os.getenv("DATABASE_URL")
    if not url or psycopg2 is None:
        return None
    return psycopg2.connect(url)

def save_audit_event(event_type: str, actor: str = "system", payload: dict | None = None):
    payload = payload or {}
    event = {
        "event_type": event_type,
        "actor": actor,
        "payload": payload,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    conn = _conn()
    if not conn:
        MEMORY_AUDIT_EVENTS.append(event)
        return {"saved": True, "backend": "memory", "event": event}
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "insert into eldora_audit_events(event_type, actor, payload) values (%s,%s,%s::jsonb)",
                    (event_type, actor, json.dumps(payload))
                )
        conn.close()
        return {"saved": True, "backend": "postgres", "event": event}
    except Exception as e:
        try:
            conn.close()
        except Exception:
            pass
        event["postgres_error"] = str(e)
        MEMORY_AUDIT_EVENTS.append(event)
        return {"saved": True, "backend": "memory_fallback", "event": event}

def save_event(topic: str, payload: dict | None = None):
    payload = payload or {}
    event = {"topic": topic, "payload": payload, "timestamp": datetime.now(timezone.utc).isoformat()}
    conn = _conn()
    if not conn:
        MEMORY_EVENT_STORE.append(event)
        return {"saved": True, "backend": "memory", "event": event}
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into eldora_event_store(topic, payload) values (%s,%s::jsonb)",
                (topic, json.dumps(payload))
            )
    conn.close()
    return {"saved": True, "backend": "postgres", "event": event}

def audit_store_report():
    total = len(MEMORY_AUDIT_EVENTS) + len(MEMORY_EVENT_STORE)
    return {
        "status": "ok",
        "events_count": total,
        "memory_audit_events": len(MEMORY_AUDIT_EVENTS),
        "memory_events": len(MEMORY_EVENT_STORE),
        "events": (MEMORY_AUDIT_EVENTS + MEMORY_EVENT_STORE)[-20:],
        "postgres_available": bool(os.getenv("DATABASE_URL") and psycopg2)
    }

