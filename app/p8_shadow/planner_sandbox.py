from typing import Any, Dict
from app.p8_shadow.real_planner import generate_hierarchical_plan
from app.p8_shadow.planner_active_policy import evaluate_planner_active_candidate

def run_limited_active_sandbox(payload: Dict[str, Any]) -> Dict[str, Any]:
    plan = generate_hierarchical_plan(payload)
    policy = evaluate_planner_active_candidate(plan)

    return {
        "capability": "HIERARCHICAL_PLANNING",
        "mode": "LIMITED_ACTIVE_SANDBOX_REVIEW",
        "plan": plan,
        "policy": policy,
        "runtime_modified": False,
        "response_modified": False,
        "state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "active_mode_enabled": False,
        "block_mode_enabled": False,
        "runtime_authority_preserved": True,
        "status": "PASS" if policy["runtime_authority_preserved"] is True else "FAIL",
    }
