from fastapi import APIRouter

from app.eldora.core.realtime_task_market import (
    create_market_task,
    submit_agent_bid,
    assign_execution_contract,
    economic_market_report
)

router = APIRouter(
    prefix="/eldora/economic-market",
    tags=["eldora-economic-market"]
)

@router.post("/task/create")
async def create_task(
    objective:str,
    priority:int=10,
    budget:int=100
):
    return create_market_task(
        objective,
        priority,
        budget
    )

@router.post("/bid/submit")
async def submit_bid(
    task_id:str,
    agent_id:str,
    estimated_cost:int=10,
    estimated_latency:int=1
):
    return submit_agent_bid(
        task_id,
        agent_id,
        estimated_cost,
        estimated_latency
    )

@router.post("/contract/assign")
async def assign_contract(
    task_id:str
):
    return assign_execution_contract(task_id)

@router.get("/report")
async def report():
    return economic_market_report()
