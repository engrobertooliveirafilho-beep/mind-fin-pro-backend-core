from fastapi import APIRouter

from app.eldora.core.autonomous_growth_runtime import (
    create_distribution_campaign,
    create_acquisition_swarm,
    execute_commercial_operation,
    optimize_revenue_route,
    autonomous_growth_report
)

router = APIRouter(
    prefix="/eldora/growth",
    tags=["eldora-growth"]
)

@router.post("/distribution/create")
async def create_distribution(
    channel:str="whatsapp",
    audience:str="general"
):
    return create_distribution_campaign(
        channel,
        audience
    )

@router.post("/swarm/create")
async def create_swarm(
    objective:str="lead_generation"
):
    return create_acquisition_swarm(
        objective
    )

@router.post("/commercial/execute")
async def execute_commercial(
    lead_id:str,
    action:str="conversion_attempt"
):
    return execute_commercial_operation(
        lead_id,
        action
    )

@router.post("/revenue/optimize")
async def optimize_revenue(
    route_name:str="primary_funnel",
    efficiency:float=1.0
):
    return optimize_revenue_route(
        route_name,
        efficiency
    )

@router.get("/report")
async def report():
    return autonomous_growth_report()
