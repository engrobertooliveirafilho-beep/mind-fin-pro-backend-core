from datetime import datetime, timezone
import uuid

SWARM_AGENTS = {}

def register_swarm_agent(agent_type:str, specialization:str):
    agent_id = str(uuid.uuid4())

    agent = {
        "agent_id":agent_id,
        "agent_type":agent_type,
        "specialization":specialization,
        "status":"active",
        "load":0.1,
        "created_at":datetime.now(timezone.utc).isoformat()
    }

    SWARM_AGENTS[agent_id] = agent

    return {
        "status":"ok",
        "agent":agent,
        "agents_total":len(SWARM_AGENTS)
    }

def swarm_report():
    return {
        "status":"ok",
        "agents_total":len(SWARM_AGENTS),
        "agents":list(SWARM_AGENTS.values())[-100:]
    }
