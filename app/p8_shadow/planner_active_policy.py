from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class PlannerActivePolicy:
    enabled: bool
    mode: str
    max_steps: int
    may_modify_response: bool
    may_modify_runtime_state: bool
    may_route: bool
    may_call_external_tools: bool

def load_planner_active_policy() -> PlannerActivePolicy:
    return PlannerActivePolicy(
        enabled=False,
        mode="LIMITED_ACTIVE_DRY_RUN",
        max_steps=5,
        may_modify_response=False,
        may_modify_runtime_state=False,
        may_route=False,
        may_call_external_tools=False,
    )

def evaluate_planner_active_candidate(plan: Dict[str, Any]) -> Dict[str, Any]:
    policy = load_planner_active_policy()
    steps = plan.get("plan", []) if isinstance(plan, dict) else []

    allowed = (
        policy.enabled is False
        and policy.may_modify_response is False
        and policy.may_modify_runtime_state is False
        and policy.may_route is False
        and policy.may_call_external_tools is False
        and len(steps) <= policy.max_steps
    )

    return {
        "policy_mode": policy.mode,
        "active_enabled": policy.enabled,
        "candidate_allowed_for_future_activation": allowed,
        "may_modify_response": policy.may_modify_response,
        "may_modify_runtime_state": policy.may_modify_runtime_state,
        "may_route": policy.may_route,
        "may_call_external_tools": policy.may_call_external_tools,
        "runtime_authority_preserved": True,
        "status": "PASS" if allowed else "REVIEW",
    }
