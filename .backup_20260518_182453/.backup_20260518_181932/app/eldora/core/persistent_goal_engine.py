from datetime import datetime, timezone
import uuid

GOALS=[]

def create_goal(goal:str, priority:int=10):
    item = {
        "goal_id":str(uuid.uuid4()),
        "goal":goal,
        "priority":priority,
        "status":"active",
        "created_at":datetime.now(timezone.utc).isoformat()
    }

    GOALS.append(item)

    return {
        "status":"ok",
        "goal":item,
        "goals_total":len(GOALS)
    }

def goal_report():
    return {
        "status":"ok",
        "goals_total":len(GOALS),
        "goals":GOALS[-100:]
    }
