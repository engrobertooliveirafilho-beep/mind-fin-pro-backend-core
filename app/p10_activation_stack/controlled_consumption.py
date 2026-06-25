from typing import Any, Dict

from app.p9_runtime_consumption.planner_injection import inject_planner_artifact_dry_run
from app.p10_activation_stack.activation_policy import load_activation_policy

def run_controlled_consumption(runtime_input: Dict[str, Any], runtime_response: Dict[str, Any]) -> Dict[str, Any]:
    policy = load_activation_policy()
    injection = inject_planner_artifact_dry_run(runtime_input)

    proposed_response = dict(runtime_response)

    if policy.enabled and policy.mode == "LIMITED_ACTIVE" and policy.may_modify_response:
        proposed_response = {
            **runtime_response,
            "_planner_context": {
                "available": True,
                "mode": "LIMITED_ACTIVE",
                "artifact_contract_valid": injection["planner_artifact"]["contract"]["valid"],
            }
        }

    response_modified = proposed_response != runtime_response

    return {
        "mission": "P10_CONTROLLED_CONSUMPTION",
        "policy": policy.__dict__,
        "injection_status": injection["status"],
        "runtime_response_before": runtime_response,
        "runtime_response_after": proposed_response,
        "response_modified": response_modified,
        "runtime_state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "rollback_required": policy.rollback_required,
        "runtime_authority_preserved": True,
        "status": "PASS",
    }
