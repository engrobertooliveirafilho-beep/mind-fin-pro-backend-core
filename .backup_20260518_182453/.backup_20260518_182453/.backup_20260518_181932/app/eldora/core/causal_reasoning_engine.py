from datetime import datetime, timezone

CAUSAL_EVENTS=[]

def causal_reasoning(cause:str, effect:str):
    item = {
        "cause":cause,
        "effect":effect,
        "confidence":0.96,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    CAUSAL_EVENTS.append(item)

    return {
        "status":"ok",
        "causal_relation":item
    }

def causal_report():
    return {
        "status":"ok",
        "events_total":len(CAUSAL_EVENTS),
        "events":CAUSAL_EVENTS[-100:]
    }
