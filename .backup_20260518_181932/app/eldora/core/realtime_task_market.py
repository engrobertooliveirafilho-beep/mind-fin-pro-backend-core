import uuid
from datetime import datetime, timezone

TASK_MARKET = []
TASK_BIDS = []
EXECUTION_CONTRACTS = []

def create_market_task(
    objective:str,
    priority:int=10,
    budget:int=100
):

    task = {
        "task_id": str(uuid.uuid4()),
        "objective": objective,
        "priority": priority,
        "budget": budget,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    TASK_MARKET.append(task)

    return {
        "status":"ok",
        "task":task,
        "market_size":len(TASK_MARKET)
    }

def submit_agent_bid(
    task_id:str,
    agent_id:str,
    estimated_cost:int=10,
    estimated_latency:int=1
):

    bid = {
        "bid_id": str(uuid.uuid4()),
        "task_id": task_id,
        "agent_id": agent_id,
        "estimated_cost": estimated_cost,
        "estimated_latency": estimated_latency,
        "score": max(1, 100 - estimated_cost - estimated_latency),
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    TASK_BIDS.append(bid)

    return {
        "status":"ok",
        "bid":bid,
        "bids_total":len(TASK_BIDS)
    }

def assign_execution_contract(task_id:str):

    bids = [b for b in TASK_BIDS if b["task_id"] == task_id]

    if not bids:
        return {
            "status":"error",
            "detail":"no bids"
        }

    best = sorted(
        bids,
        key=lambda x: x["score"],
        reverse=True
    )[0]

    contract = {
        "contract_id": str(uuid.uuid4()),
        "task_id": task_id,
        "assigned_agent": best["agent_id"],
        "score": best["score"],
        "status": "assigned",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    EXECUTION_CONTRACTS.append(contract)

    return {
        "status":"ok",
        "contract":contract
    }

def economic_market_report():

    return {
        "status":"ok",
        "tasks_total":len(TASK_MARKET),
        "bids_total":len(TASK_BIDS),
        "contracts_total":len(EXECUTION_CONTRACTS),
        "tasks":TASK_MARKET[-20:],
        "contracts":EXECUTION_CONTRACTS[-20:]
    }
