from datetime import datetime, timezone

LIVE_AGENTS=[]

def activate_agent(agent:str, runtime:str):
    item = {
        "agent":agent,
        "runtime":runtime,
        "status":"active",
        "distributed":True,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    LIVE_AGENTS.append(item)

    return {
        "status":"ok",
        "agent_runtime":item
    }

def agent_report():
    return {
        "status":"ok",
        "agents_total":len(LIVE_AGENTS),
        "agents":LIVE_AGENTS[-100:]
    }
