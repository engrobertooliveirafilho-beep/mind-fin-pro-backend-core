from typing import Any, Dict, List
from app.p8_shadow.planner_sandbox import run_limited_active_sandbox

REQUIRED_PLAN_FIELDS = {
    "capability",
    "mode",
    "goal",
    "depth",
    "step_count",
    "plan",
    "execution_tree",
    "runtime_modified",
    "response_modified",
    "runtime_authority_preserved",
}

def validate_planner_consumption_contract(plan: Dict[str, Any]) -> Dict[str, Any]:
    missing = sorted([field for field in REQUIRED_PLAN_FIELDS if field not in plan])
    plan_steps = plan.get("plan", [])

    valid_steps = isinstance(plan_steps, list) and all(
        isinstance(step, dict)
        and "title" in step
        and "objective" in step
        and "depends_on" in step
        and "risk" in step
        and "validation" in step
        for step in plan_steps
    )

    valid = (
        not missing
        and valid_steps
        and plan.get("runtime_modified") is False
        and plan.get("response_modified") is False
        and plan.get("runtime_authority_preserved") is True
    )

    return {
        "contract": "P8_PLANNER_SANDBOX_CONSUMPTION_CONTRACT",
        "valid": valid,
        "missing_fields": missing,
        "valid_steps": valid_steps,
        "runtime_modified": False,
        "response_modified": False,
        "runtime_authority_preserved": True,
        "status": "PASS" if valid else "FAIL",
    }

def produce_consumable_planner_artifact(payload: Dict[str, Any]) -> Dict[str, Any]:
    sandbox = run_limited_active_sandbox(payload)
    plan = sandbox["plan"]
    contract = validate_planner_consumption_contract(plan)

    return {
        "artifact_type": "PLANNER_SANDBOX_CONSUMABLE_OUTPUT",
        "contract": contract,
        "planner_output": plan,
        "consumption_allowed": contract["valid"],
        "runtime_modified": False,
        "response_modified": False,
        "active_mode_enabled": False,
        "block_mode_enabled": False,
        "runtime_authority_preserved": True,
        "status": "PASS" if contract["valid"] else "FAIL",
    }
