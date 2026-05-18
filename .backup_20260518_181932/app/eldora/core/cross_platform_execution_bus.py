from datetime import datetime, timezone

BUS_EVENTS=[]

def route_execution(source:str, target:str, task:str):
    item = {
        "source":source,
        "target":target,
        "task":task,
        "status":"routed",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    BUS_EVENTS.append(item)

    return {
        "status":"ok",
        "event":item
    }

def bus_report():
    return {
        "status":"ok",
        "events_total":len(BUS_EVENTS),
        "events":BUS_EVENTS[-100:]
    }
