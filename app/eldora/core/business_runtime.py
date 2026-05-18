import uuid

from datetime import datetime, timezone

BUSINESS_AGENTS = []
LEAD_PIPELINE = []
REVENUE_EVENTS = []

def create_business_agent(
    agent_name:str,
    specialization:str="sales"
):

    agent = {
        "agent_id": str(uuid.uuid4()),
        "agent_name": agent_name,
        "specialization": specialization,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    BUSINESS_AGENTS.append(agent)

    return {
        "status":"ok",
        "agent":agent,
        "agents_total":len(BUSINESS_AGENTS)
    }

def create_lead(
    name:str,
    source:str="web"
):

    lead = {
        "lead_id": str(uuid.uuid4()),
        "name": name,
        "source": source,
        "status": "captured",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    LEAD_PIPELINE.append(lead)

    return {
        "status":"ok",
        "lead":lead,
        "leads_total":len(LEAD_PIPELINE)
    }

def register_revenue_event(
    lead_id:str,
    value:float,
    event_type:str="conversion"
):

    event = {
        "event_id": str(uuid.uuid4()),
        "lead_id": lead_id,
        "value": value,
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    REVENUE_EVENTS.append(event)

    return {
        "status":"ok",
        "event":event,
        "revenue_events":len(REVENUE_EVENTS)
    }

def business_runtime_report():

    total_revenue = sum(
        x["value"] for x in REVENUE_EVENTS
    )

    return {
        "status":"ok",
        "agents_total":len(BUSINESS_AGENTS),
        "leads_total":len(LEAD_PIPELINE),
        "revenue_events":len(REVENUE_EVENTS),
        "total_revenue":total_revenue,
        "agents":BUSINESS_AGENTS[-20:],
        "leads":LEAD_PIPELINE[-20:]
    }
