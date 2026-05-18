from fastapi import APIRouter

from app.eldora.core.live_browser_agents import (
    activate_browser_agent,
    browser_report
)

from app.eldora.core.autonomous_digital_presence import (
    digital_presence,
    presence_report
)

from app.eldora.core.internet_awareness_engine import (
    internet_awareness,
    awareness_report
)

router = APIRouter(
    prefix="/eldora/embodied",
    tags=["eldora-embodied"]
)

@router.post("/browser/activate")
async def browser(agent:str, objective:str):
    return activate_browser_agent(agent, objective)

@router.get("/browser/report")
async def browsers():
    return browser_report()

@router.post("/presence/activate")
async def presence(identity:str, platform:str):
    return digital_presence(identity, platform)

@router.get("/presence/report")
async def presences():
    return presence_report()

@router.post("/awareness/signal")
async def awareness(source:str, signal:str):
    return internet_awareness(source, signal)

@router.get("/awareness/report")
async def awareness_runtime():
    return awareness_report()
