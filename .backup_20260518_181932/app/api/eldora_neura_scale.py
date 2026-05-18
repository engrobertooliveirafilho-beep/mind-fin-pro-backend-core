from fastapi import APIRouter

from app.eldora.core.neura_scale_runtime import (
    create_tenant,
    create_whatsapp_acquisition_campaign,
    schedule_cognition_workload,
    activate_public_launch,
    neura_scale_report
)

router = APIRouter(
    prefix="/eldora/neura-scale",
    tags=["eldora-neura-scale"]
)

@router.post("/tenant/create")
async def tenant(name:str, plan:str="starter"):
    return create_tenant(name, plan)

@router.post("/acquisition/whatsapp")
async def acquisition(audience:str, offer:str):
    return create_whatsapp_acquisition_campaign(audience, offer)

@router.post("/scheduler/cost-aware")
async def scheduler(workload:str, max_cost:float=1.0, priority:int=10):
    return schedule_cognition_workload(workload, max_cost, priority)

@router.post("/launch/public")
async def launch(product:str="NEURA", market:str="students"):
    return activate_public_launch(product, market)

@router.get("/report")
async def report():
    return neura_scale_report()
