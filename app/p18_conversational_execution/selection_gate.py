from typing import Dict, Any
from app.p18_conversational_execution.response_executor import execute_conversational_response
from app.p18_conversational_execution.shadow_diff import compare_runtime_vs_shadow

def run_limited_internal_selection_gate(message: str, runtime_response: Dict[str, Any]) -> Dict[str, Any]:
    candidate = execute_conversational_response(message)
    diff = compare_runtime_vs_shadow(message, runtime_response, {"answer": candidate["answer"]})

    recommendation = "USE_CANDIDATE_INTERNAL_ONLY" if diff["candidate_better"] else "KEEP_RUNTIME"

    return {
        "mission": "P18D_LIMITED_INTERNAL_SELECTION_GATE",
        "message": message,
        "runtime_response": runtime_response,
        "candidate_response": {"answer": candidate["answer"]},
        "diff": diff,
        "recommendation": recommendation,
        "selected_response": runtime_response,
        "candidate_visible_to_user": False,
        "runtime_response_modified": False,
        "runtime_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "production_enabled": False,
        "status": "PASS",
    }
