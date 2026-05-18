from fastapi import APIRouter

from app.eldora.core.world_model_engine import (
    create_world_state,
    world_report
)

from app.eldora.core.causal_reasoning_engine import (
    causal_reasoning,
    causal_report
)

from app.eldora.core.predictive_simulation_engine import (
    run_simulation,
    simulation_report
)

router = APIRouter(
    prefix="/eldora/world",
    tags=["eldora-world"]
)

@router.post("/state/create")
async def state(environment:str, context:str):
    return create_world_state(environment, context)

@router.get("/state/report")
async def states():
    return world_report()

@router.post("/causal/reason")
async def causal(cause:str, effect:str):
    return causal_reasoning(cause, effect)

@router.get("/causal/report")
async def causal_runtime():
    return causal_report()

@router.post("/simulation/run")
async def simulation(goal:str, variables:str):
    return run_simulation(goal, variables)

@router.get("/simulation/report")
async def simulation_runtime():
    return simulation_report()
