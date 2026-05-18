from fastapi import APIRouter

from app.eldora.core.autonomous_planner import (
    create_plan,
    get_plan,
    planner_report
)

from app.eldora.core.governor_engine import (
    governor_check,
    consume_budget
)

from app.eldora.core.checkpoint_engine import (
    create_checkpoint,
    checkpoint_report
)

router = APIRouter(prefix="/eldora/autonomous", tags=["eldora-autonomous"])

@router.post("/plan/create")
async def plan_create(goal: str = "default_goal"):
    return create_plan(goal)

@router.get("/plan/get")
async def plan_get(plan_id: str):
    return get_plan(plan_id)

@router.get("/planner/report")
async def planner():
    return planner_report()

@router.get("/governor/check")
async def governor():
    return governor_check()

@router.post("/governor/consume")
async def governor_consume(amount: int = 1):
    return consume_budget(amount)

@router.post("/checkpoint/create")
async def checkpoint():
    return create_checkpoint({
        "runtime": "eldora",
        "status": "operational"
    })

@router.get("/checkpoint/report")
async def checkpoints():
    return checkpoint_report()
