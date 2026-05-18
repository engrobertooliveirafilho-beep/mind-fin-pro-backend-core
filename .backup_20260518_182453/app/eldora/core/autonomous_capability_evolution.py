from datetime import datetime, timezone

EVOLUTION_LOG=[]

def evolve_capability(capability:str, improvement:str):
    item = {
        "capability":capability,
        "improvement":improvement,
        "evolution_score":0.98,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    EVOLUTION_LOG.append(item)

    return {
        "status":"ok",
        "evolution":item
    }

def evolution_report():
    return {
        "status":"ok",
        "events_total":len(EVOLUTION_LOG),
        "events":EVOLUTION_LOG[-50:]
    }
