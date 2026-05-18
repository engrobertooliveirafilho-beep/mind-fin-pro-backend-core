from datetime import datetime, timezone

BROWSER_AGENTS=[]

def activate_browser_agent(agent:str, objective:str):
    item = {
        "agent":agent,
        "objective":objective,
        "status":"navigating",
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

    BROWSER_AGENTS.append(item)

    return {
        "status":"ok",
        "browser_agent":item
    }

def browser_report():
    return {
        "status":"ok",
        "agents_total":len(BROWSER_AGENTS),
        "agents":BROWSER_AGENTS[-100:]
    }
