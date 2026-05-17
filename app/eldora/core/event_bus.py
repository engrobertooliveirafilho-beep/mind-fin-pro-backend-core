EVENTS = []

def publish(topic: str, payload: dict):
    event = {"topic": topic, "payload": payload}
    EVENTS.append(event)
    return event

def event_bus_report():
    return {"status": "ok", "events_count": len(EVENTS), "events": EVENTS[-20:]}
