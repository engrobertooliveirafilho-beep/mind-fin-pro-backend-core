from fastapi import APIRouter

from app.eldora.core.distributed_swarm_engine import (
    register_swarm_agent,
    swarm_report
)

from app.eldora.core.economic_governor import (
    consume_budget,
    governor_report
)

from app.eldora.core.cognitive_load_balancer import (
    balance_cognitive_load,
    load_report
)

router = APIRouter(
    prefix="/eldora/swarm",
    tags=["eldora-swarm"]
)

@router.post("/agent/register")
async def register(agent_type:str, specialization:str):
    return register_swarm_agent(agent_type, specialization)

@router.get("/agents/report")
async def agents():
    return swarm_report()

@router.post("/governor/consume")
async def consume(amount:int=1):
    return consume_budget(amount)

@router.get("/governor/report")
async def governor():
    return governor_report()

@router.post("/load/balance")
async def balance(node:str, load:float):
    return balance_cognitive_load(node, load)

@router.get("/load/report")
async def balancing():
    return load_report()
