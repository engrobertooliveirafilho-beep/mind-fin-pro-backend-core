from datetime import datetime, timezone

EXECUTION_BUDGET = {
    "max_budget":1000,
    "used_budget":0,
    "remaining_budget":1000
}

def consume_budget(amount:int):
    EXECUTION_BUDGET["used_budget"] += amount
    EXECUTION_BUDGET["remaining_budget"] -= amount

    return {
        "status":"ok",
        "budget":EXECUTION_BUDGET,
        "timestamp":datetime.now(timezone.utc).isoformat()
    }

def governor_report():
    return {
        "status":"ok",
        "budget":EXECUTION_BUDGET
    }
