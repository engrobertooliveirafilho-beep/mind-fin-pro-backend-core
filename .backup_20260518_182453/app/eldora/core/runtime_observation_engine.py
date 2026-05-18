from datetime import datetime, timezone

OBSERVATION_EVENTS=[]

def observe_environment(environment:str, signal:str):
    item = {
        "environment":environment,
        "signal":signal,
        "awareness":0.95,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    OBSERVATION_EVENTS.append(item)

    return {
        "status":"ok",
        "observation":item
    }

def observation_report():
    return {
        "status":"ok",
        "events_total":len(OBSERVATION_EVENTS),
        "events":OBSERVATION_EVENTS[-100:]
    }
