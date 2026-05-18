from datetime import datetime, timezone

ORCHESTRATIONS=[]

def orchestrate_agents(agent_group:str, objective:str):
    item = {
        "agent_group":agent_group,
        "objective":objective,
        "status":"orchestrated",
        "runtime":"distributed",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    ORCHESTRATIONS.append(item)

    return {
        "status":"ok",
        "orchestration":item
    }

def orchestration_report():
    return {
        "status":"ok",
        "orchestrations_total":len(ORCHESTRATIONS),
        "orchestrations":ORCHESTRATIONS[-100:]
    }
