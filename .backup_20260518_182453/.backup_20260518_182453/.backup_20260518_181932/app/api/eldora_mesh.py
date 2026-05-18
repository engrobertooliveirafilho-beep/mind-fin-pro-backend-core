from fastapi import APIRouter

from app.eldora.core.realtime_cognitive_mesh import (
    sync_mesh,
    mesh_report
)

from app.eldora.core.event_broker_fabric import (
    broker_event,
    broker_report
)

from app.eldora.core.live_agent_cloud import (
    activate_agent,
    agent_report
)

router = APIRouter(
    prefix="/eldora/mesh",
    tags=["eldora-mesh"]
)

@router.post("/sync")
async def sync(node:str, cognition:str):
    return sync_mesh(node, cognition)

@router.get("/sync/report")
async def mesh():
    return mesh_report()

@router.post("/broker/publish")
async def broker(channel:str, payload:str):
    return broker_event(channel, payload)

@router.get("/broker/report")
async def brokers():
    return broker_report()

@router.post("/agent/activate")
async def agent(agent:str, runtime:str):
    return activate_agent(agent, runtime)

@router.get("/agent/report")
async def agents():
    return agent_report()
