from datetime import datetime, timezone

EMOTIONAL_EVENTS=[]

def emotional_continuity(user_id:str, emotion:str, context:str):
    item = {
        "user_id":user_id,
        "emotion":emotion,
        "context":context,
        "continuity_score":0.95,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    EMOTIONAL_EVENTS.append(item)

    return {
        "status":"ok",
        "event":item
    }

def emotional_report():
    return {
        "status":"ok",
        "events_total":len(EMOTIONAL_EVENTS),
        "events":EMOTIONAL_EVENTS[-100:]
    }
