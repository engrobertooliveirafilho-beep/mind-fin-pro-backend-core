from fastapi import APIRouter

from app.eldora.core.self_healing_engine import (
    trigger_recovery,
    healing_report
)

from app.eldora.core.supervisor_swarm import (
    supervisor_report
)

from app.eldora.core.recursive_execution_engine import (
    recursive_execute,
    recursive_report
)

router = APIRouter(prefix="/eldora/runtime", tags=["eldora-runtime"])

@router.post("/self-heal")
async def self_heal(component: str = "runtime"):
    return trigger_recovery(component)

@router.get("/self-heal/report")
async def self_heal_report():
    return healing_report()

@router.get("/supervisor/report")
async def supervisor():
    return supervisor_report()

@router.post("/recursive/execute")
async def recursive(goal: str = "runtime_validation", max_depth: int = 3):
    return recursive_execute(goal, 1, max_depth)

@router.get("/recursive/report")
async def recursive_runtime():
    return recursive_report()
