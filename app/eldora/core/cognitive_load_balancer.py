from datetime import datetime, timezone

LOAD_EVENTS=[]

def balance_cognitive_load(node:str, load:float):
    item = {
        "node":node,
        "load":load,
        "balanced":True,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    LOAD_EVENTS.append(item)

    return {
        "status":"ok",
        "event":item
    }

def load_report():
    return {
        "status":"ok",
        "events_total":len(LOAD_EVENTS),
        "events":LOAD_EVENTS[-100:]
    }
