import uuid
from datetime import datetime, timezone

def new_correlation_id():
    return str(uuid.uuid4())

def telemetry_event(name: str, payload: dict | None = None):
    return {
        "name": name,
        "payload": payload or {},
        "correlation_id": new_correlation_id(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
