from typing import Dict, Any

def evaluate_p12_risk(record: Dict[str, Any]) -> Dict[str, Any]:
    hard_blocks = [
        record.get("runtime_state_modified") is True,
        record.get("routes_modified") is True,
        record.get("dispatcher_modified") is True,
        record.get("whatsapp_webhook_modified") is True,
    ]

    return {
        "mission": "P12_RISK_GOVERNANCE",
        "risk_level": "BLOCKED" if any(hard_blocks) else "LOW",
        "activation_allowed": not any(hard_blocks),
        "blocking_reasons": ["core_mutation_detected"] if any(hard_blocks) else [],
        "status": "PASS" if not any(hard_blocks) else "FAIL",
    }
