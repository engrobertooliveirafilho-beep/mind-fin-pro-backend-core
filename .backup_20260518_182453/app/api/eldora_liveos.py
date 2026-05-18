from fastapi import APIRouter

from app.eldora.core.realtime_event_stream import (
    publish_event,
    stream_report
)

from app.eldora.core.universal_orchestration_fabric import (
    orchestrate_agents,
    orchestration_report
)

from app.eldora.core.live_operating_system_engine import (
    runtime_signal,
    runtime_report
)

router = APIRouter(
    prefix="/eldora/liveos",
    tags=["eldora-liveos"]
)

@router.post("/stream/publish")
async def publish(stream:str, event:str):
    return publish_event(stream, event)

@router.get("/stream/report")
async def streams():
    return stream_report()

@router.post("/orchestrate")
async def orchestrate(agent_group:str, objective:str):
    return orchestrate_agents(agent_group, objective)

@router.get("/orchestrate/report")
async def orchestrations():
    return orchestration_report()

@router.post("/runtime/signal")
async def runtime(environment:str, signal:str):
    return runtime_signal(environment, signal)

@router.get("/runtime/report")
async def runtimes():
    return runtime_report()
