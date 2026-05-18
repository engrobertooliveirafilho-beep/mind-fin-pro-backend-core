from fastapi import APIRouter

from app.eldora.core.live_connector_fabric import (
    register_connector,
    connector_report
)

from app.eldora.core.cross_platform_execution_bus import (
    route_execution,
    bus_report
)

from app.eldora.core.infrastructure_event_engine import (
    infrastructure_event,
    infrastructure_report
)

router = APIRouter(
    prefix="/eldora/infrastructure",
    tags=["eldora-infrastructure"]
)

@router.post("/connector/register")
async def connector(platform:str, capability:str):
    return register_connector(platform, capability)

@router.get("/connector/report")
async def connectors():
    return connector_report()

@router.post("/bus/route")
async def route(source:str, target:str, task:str):
    return route_execution(source, target, task)

@router.get("/bus/report")
async def bus():
    return bus_report()

@router.post("/event/create")
async def event(environment:str, signal:str):
    return infrastructure_event(environment, signal)

@router.get("/event/report")
async def events():
    return infrastructure_report()
