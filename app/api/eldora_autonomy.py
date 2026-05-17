from fastapi import APIRouter

from app.eldora.core.persistent_goal_engine import (
    create_goal,
    goal_report
)

from app.eldora.core.continuous_execution_engine import (
    execute_loop,
    loop_report
)

from app.eldora.core.runtime_observation_engine import (
    observe_environment,
    observation_report
)

router = APIRouter(
    prefix="/eldora/autonomy",
    tags=["eldora-autonomy"]
)

@router.post("/goal/create")
async def goal(goal:str, priority:int=10):
    return create_goal(goal, priority)

@router.get("/goal/report")
async def goals():
    return goal_report()

@router.post("/loop/execute")
async def loop(mission:str):
    return execute_loop(mission)

@router.get("/loop/report")
async def loops():
    return loop_report()

@router.post("/observe")
async def observe(environment:str, signal:str):
    return observe_environment(environment, signal)

@router.get("/observe/report")
async def observations():
    return observation_report()
