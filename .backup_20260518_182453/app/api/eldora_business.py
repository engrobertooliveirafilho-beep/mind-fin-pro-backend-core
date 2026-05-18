from fastapi import APIRouter

from app.eldora.core.business_runtime import (
    create_business_agent,
    create_lead,
    register_revenue_event,
    business_runtime_report
)

router = APIRouter(
    prefix="/eldora/business",
    tags=["eldora-business"]
)

@router.post("/agent/create")
async def create_agent(
    agent_name:str,
    specialization:str="sales"
):
    return create_business_agent(
        agent_name,
        specialization
    )

@router.post("/lead/create")
async def create_pipeline_lead(
    name:str,
    source:str="web"
):
    return create_lead(
        name,
        source
    )

@router.post("/revenue/register")
async def register_revenue(
    lead_id:str,
    value:float,
    event_type:str="conversion"
):
    return register_revenue_event(
        lead_id,
        value,
        event_type
    )

@router.get("/report")
async def report():
    return business_runtime_report()
