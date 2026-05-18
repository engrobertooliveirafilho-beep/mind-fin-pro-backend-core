from fastapi import APIRouter
from app.eldora.core.task_engine import create_task, get_task, task_report
from app.eldora.core.agent_orchestrator import orchestrate
from app.eldora.core.distributed_runtime import distributed_runtime_report

router = APIRouter(prefix="/eldora/async", tags=["eldora-async"])

@router.post("/task/create")
async def task_create(task_type: str = "generic", payload: str = "ok"):
    return create_task(task_type, {"payload": payload})

@router.get("/task/get")
async def task_get(task_id: str):
    return get_task(task_id)

@router.get("/tasks/report")
async def tasks_report():
    return task_report()

@router.post("/orchestrate")
async def orchestrator(goal: str = "default_goal"):
    return orchestrate(goal)

@router.get("/runtime/distributed")
async def distributed_runtime():
    return distributed_runtime_report()
