from datetime import datetime, timezone

RELATIONAL_COGNITION=[]

def relational_analysis(user_id:str, profile:str):
    item = {
        "user_id":user_id,
        "profile":profile,
        "relationship_depth":0.94,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    RELATIONAL_COGNITION.append(item)

    return {
        "status":"ok",
        "analysis":item
    }

def relational_report():
    return {
        "status":"ok",
        "events_total":len(RELATIONAL_COGNITION),
        "events":RELATIONAL_COGNITION[-100:]
    }
