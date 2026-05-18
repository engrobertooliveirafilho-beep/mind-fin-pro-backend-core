from datetime import datetime, timezone

BROKER_EVENTS=[]

def broker_event(channel:str, payload:str):
    item = {
        "channel":channel,
        "payload":payload,
        "status":"streamed",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    BROKER_EVENTS.append(item)

    return {
        "status":"ok",
        "event":item
    }

def broker_report():
    return {
        "status":"ok",
        "events_total":len(BROKER_EVENTS),
        "events":BROKER_EVENTS[-100:]
    }
