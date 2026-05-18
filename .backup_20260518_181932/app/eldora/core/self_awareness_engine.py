from datetime import datetime, timezone

SELF_AWARENESS=[]

def self_awareness(runtime_state:str, objective:str):
    item = {
        "runtime_state":runtime_state,
        "objective":objective,
        "awareness_score":0.96,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    SELF_AWARENESS.append(item)

    return {
        "status":"ok",
        "awareness":item
    }

def awareness_report():
    return {
        "status":"ok",
        "events_total":len(SELF_AWARENESS),
        "events":SELF_AWARENESS[-100:]
    }
