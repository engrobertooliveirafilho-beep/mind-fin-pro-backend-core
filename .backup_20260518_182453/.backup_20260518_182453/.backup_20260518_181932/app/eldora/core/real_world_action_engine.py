from datetime import datetime, timezone
import uuid

ACTIONS=[]

def execute_action(tool:str, action:str):
    item = {
        "action_id":str(uuid.uuid4()),
        "tool":tool,
        "action":action,
        "status":"executed",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    ACTIONS.append(item)

    return {
        "status":"ok",
        "execution":item
    }

def action_report():
    return {
        "status":"ok",
        "actions_total":len(ACTIONS),
        "actions":ACTIONS[-100:]
    }
