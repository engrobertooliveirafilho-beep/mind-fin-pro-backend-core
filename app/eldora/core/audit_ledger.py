from app.eldora.core.persistent_event_store import save_audit_event, audit_store_report

def audit_event(event_type: str, actor: str = "system", payload: dict | None = None):
    return save_audit_event(event_type, actor, payload)

def audit_report():
    return audit_store_report()
