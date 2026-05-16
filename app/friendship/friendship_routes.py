from fastapi import APIRouter
from .proactive_scheduler import plan_checkin
router=APIRouter(prefix="/friendship", tags=["friendship"])
@router.post("/checkin/plan")
async def checkin_plan(payload:dict):
    return plan_checkin(payload.get("profile",{}), payload.get("memory",{}))
