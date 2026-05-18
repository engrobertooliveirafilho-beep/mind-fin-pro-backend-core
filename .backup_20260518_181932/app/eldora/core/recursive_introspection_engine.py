from datetime import datetime, timezone

INTROSPECTION_LOG=[]

def recursive_introspection(layer:str, reflection:str):
    item = {
        "layer":layer,
        "reflection":reflection,
        "recursive_depth":3,
        "confidence":0.95,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    INTROSPECTION_LOG.append(item)

    return {
        "status":"ok",
        "introspection":item
    }

def introspection_report():
    return {
        "status":"ok",
        "events_total":len(INTROSPECTION_LOG),
        "events":INTROSPECTION_LOG[-100:]
    }
