import uuid

from datetime import datetime, timezone

BROWSER_FLEET = []
BROWSER_TASKS = []
BROWSER_SESSIONS = []

def create_browser_agent(
    agent_name:str,
    capability:str="navigation"
):

    agent = {
        "agent_id": str(uuid.uuid4()),
        "agent_name": agent_name,
        "capability": capability,
        "status": "idle",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    BROWSER_FLEET.append(agent)

    return {
        "status":"ok",
        "agent":agent,
        "fleet_total":len(BROWSER_FLEET)
    }

def create_browser_task(
    objective:str,
    target_url:str
):

    task = {
        "task_id": str(uuid.uuid4()),
        "objective": objective,
        "target_url": target_url,
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    BROWSER_TASKS.append(task)

    return {
        "status":"ok",
        "task":task,
        "tasks_total":len(BROWSER_TASKS)
    }

def assign_browser_task(
    task_id:str,
    agent_id:str
):

    session = {
        "session_id": str(uuid.uuid4()),
        "task_id": task_id,
        "agent_id": agent_id,
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    BROWSER_SESSIONS.append(session)

    return {
        "status":"ok",
        "session":session,
        "sessions_total":len(BROWSER_SESSIONS)
    }

def browser_fleet_report():

    return {
        "status":"ok",
        "fleet_total":len(BROWSER_FLEET),
        "tasks_total":len(BROWSER_TASKS),
        "sessions_total":len(BROWSER_SESSIONS),
        "fleet":BROWSER_FLEET[-20:],
        "sessions":BROWSER_SESSIONS[-20:]
    }
