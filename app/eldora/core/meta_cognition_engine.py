from datetime import datetime, timezone
import uuid

META_COGNITION_EVENTS=[]

def analyze_internal_state(runtime:str, cognition:str):
    event = {
        "event_id":str(uuid.uuid4()),
        "runtime":runtime,
        "cognition":cognition,
        "self_score":0.97,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

    META_COGNITION_EVENTS.append(event)

    return {
        "status":"ok",
        "analysis":event
    }

def meta_cognition_report():
    return {
        "status":"ok",
        "events_total":len(META_COGNITION_EVENTS),
        "events":META_COGNITION_EVENTS[-100:]
    }
