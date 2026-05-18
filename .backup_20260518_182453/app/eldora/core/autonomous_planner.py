from datetime import datetime, timezone
import uuid

PLANS = {}

def create_plan(goal: str):
    plan_id = str(uuid.uuid4())

    plan = {
        "plan_id": plan_id,
        "goal": goal,
        "steps": [
            "memory_analysis",
            "retrieval_execution",
            "reasoning_execution",
            "execution_runtime"
        ],
        "status": "planned",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    PLANS[plan_id] = plan
    return plan

def get_plan(plan_id: str):
    return PLANS.get(plan_id, {"status": "not_found"})

def planner_report():
    return {
        "status": "ok",
        "plans_total": len(PLANS),
        "plans": list(PLANS.values())[-20:]
    }
