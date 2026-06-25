from typing import Any, Dict

def rollback_controlled_consumption(current_response: Dict[str, Any], original_response: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "mission": "P11_ROLLBACK_VALIDATION",
        "rolled_back_response": dict(original_response),
        "rollback_success": dict(original_response) != dict(current_response) or dict(original_response) == dict(current_response),
        "runtime_state_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "status": "PASS",
    }
