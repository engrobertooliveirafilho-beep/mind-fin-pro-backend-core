from app.eldora.core.persistent_event_store import save_event, audit_store_report

def publish(topic: str, payload: dict):
    return save_event(topic, payload)

def event_bus_report():
    return audit_store_report()
