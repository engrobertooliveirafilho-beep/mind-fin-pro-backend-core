from typing import Any, Dict

from app.p8_shadow.planner_consumption_contract import produce_consumable_planner_artifact
from app.p9_runtime_consumption.consumption_gate import load_runtime_consumption_gate
from app.p9_runtime_consumption.context_bridge import build_read_only_runtime_context

def inject_planner_artifact_dry_run(runtime_input: Dict[str, Any]) -> Dict[str, Any]:
    gate = load_runtime_consumption_gate()
    context = build_read_only_runtime_context(runtime_input)
    artifact = produce_consumable_planner_artifact(runtime_input)

    consumption_allowed = (
        gate.enabled is True
        and gate.mode in {"DRY_RUN", "INTERNAL"}
        and artifact["consumption_allowed"] is True
        and gate.may_modify_response is False
        and gate.may_modify_runtime_state is False
        and gate.may_modify_routes is False
        and gate.may_modify_dispatcher is False
    )

    return {
        "mission": "P9_PLANNER_ARTIFACT_INJECTION_DRY_RUN",
        "gate": gate.__dict__,
        "context": context,
        "planner_artifact": artifact,
        "consumption_allowed": consumption_allowed,
        "runtime_response_modified": False,
        "runtime_state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "runtime_authority_preserved": True,
        "status": "PASS" if consumption_allowed else "SKIPPED",
    }
