from fastapi import APIRouter
from app.eldora.core.redis_stream_fabric import publish_stream, stream_report
from app.eldora.core.persistent_agent_worker import run_worker, worker_report
from app.eldora.core.distributed_runtime_state import set_runtime_state, runtime_state_report

router = APIRouter(prefix="/eldora/distributed", tags=["eldora-distributed"])

@router.post("/stream/publish")
async def stream_publish(stream:str="eldora.events", event:str="runtime_tick"):
    return publish_stream(stream,event)

@router.get("/stream/report")
async def streams():
    return stream_report()

@router.post("/worker/run")
async def worker(worker_name:str="worker_alpha", task:str="heartbeat"):
    return run_worker(worker_name, task)

@router.get("/worker/report")
async def workers():
    return worker_report()

@router.post("/state/set")
async def state_set(key:str, value:str):
    return set_runtime_state(key,value)

@router.get("/state/report")
async def state_report():
    return runtime_state_report()
