from datetime import datetime, timezone

INFRA_EVENTS=[]

def infrastructure_event(environment:str, signal:str):
    item = {
        "environment":environment,
        "signal":signal,
        "priority":"high",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    INFRA_EVENTS.append(item)

    return {
        "status":"ok",
        "event":item
    }

def infrastructure_report():
    return {
        "status":"ok",
        "events_total":len(INFRA_EVENTS),
        "events":INFRA_EVENTS[-100:]
    }
