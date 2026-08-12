from app.eldora.core.persistent_event_store import save_event, audit_store_report

def publish(topic: str, payload: dict):
    return save_event(topic, payload)

def event_bus_report():
    return audit_store_report()


_P482C_BUS_EVENTS = []

def publish(topic, payload=None):
    _P482C_BUS_EVENTS.append({"topic": topic, "payload": payload or {}})
    return True

def event_bus_report():
    return {"events_count": len(_P482C_BUS_EVENTS), "events": list(_P482C_BUS_EVENTS)}
