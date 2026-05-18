from fastapi import APIRouter

from app.eldora.core.browser_fleet_runtime import (
    create_browser_agent,
    create_browser_task,
    assign_browser_task,
    browser_fleet_report
)

router = APIRouter(
    prefix="/eldora/browser-fleet",
    tags=["eldora-browser-fleet"]
)

@router.post("/agent/create")
async def create_agent(
    agent_name:str,
    capability:str="navigation"
):
    return create_browser_agent(
        agent_name,
        capability
    )

@router.post("/task/create")
async def create_task(
    objective:str,
    target_url:str
):
    return create_browser_task(
        objective,
        target_url
    )

@router.post("/task/assign")
async def assign_task(
    task_id:str,
    agent_id:str
):
    return assign_browser_task(
        task_id,
        agent_id
    )

@router.get("/report")
async def report():
    return browser_fleet_report()
