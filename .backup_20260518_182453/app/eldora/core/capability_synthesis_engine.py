from datetime import datetime, timezone
import uuid

CAPABILITY_REGISTRY = {}

def synthesize_capability(name:str, objective:str):
    capability_id = str(uuid.uuid4())

    capability = {
        "capability_id": capability_id,
        "name": name,
        "objective": objective,
        "status": "generated",
        "score": 0.95,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    CAPABILITY_REGISTRY[capability_id] = capability

    return {
        "status":"ok",
        "capability":capability,
        "capabilities_total":len(CAPABILITY_REGISTRY)
    }

def capability_report():
    return {
        "status":"ok",
        "capabilities_total":len(CAPABILITY_REGISTRY),
        "capabilities":list(CAPABILITY_REGISTRY.values())[-50:]
    }
