from datetime import datetime, timezone

GOVERNOR_STATE = {
    "execution_budget": 100,
    "max_loops": 10,
    "active_loops": 0
}

def governor_check():
    return {
        "status": "ok",
        "state": GOVERNOR_STATE
    }

def consume_budget(amount: int = 1):
    GOVERNOR_STATE["execution_budget"] -= amount
    GOVERNOR_STATE["active_loops"] += 1

    allowed = (
        GOVERNOR_STATE["execution_budget"] > 0 and
        GOVERNOR_STATE["active_loops"] <= GOVERNOR_STATE["max_loops"]
    )

    return {
        "status": "ok",
        "allowed": allowed,
        "execution_budget": GOVERNOR_STATE["execution_budget"],
        "active_loops": GOVERNOR_STATE["active_loops"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
