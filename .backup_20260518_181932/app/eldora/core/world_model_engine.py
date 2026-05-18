from datetime import datetime, timezone
import uuid

WORLD_STATES=[]

def create_world_state(environment:str, context:str):
    state = {
        "state_id":str(uuid.uuid4()),
        "environment":environment,
        "context":context,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

    WORLD_STATES.append(state)

    return {
        "status":"ok",
        "state":state,
        "states_total":len(WORLD_STATES)
    }

def world_report():
    return {
        "status":"ok",
        "states_total":len(WORLD_STATES),
        "states":WORLD_STATES[-100:]
    }
