from typing import Any, Dict
from .telemetry import stable_hash

def build_decision_diff(
    *,
    request_id: str,
    runtime_decision: Any,
    oversight_decision: Any,
    confidence: float = 0.0,
    reason: str = "",
) -> Dict[str, Any]:
    runtime_hash = stable_hash(runtime_decision)
    oversight_hash = stable_hash(oversight_decision)

    return {
        "request_id": request_id,
        "runtime_decision_hash": runtime_hash,
        "oversight_decision_hash": oversight_hash,
        "same_decision": runtime_hash == oversight_hash,
        "confidence": confidence,
        "divergence_score": 0.0 if runtime_hash == oversight_hash else 1.0,
        "reason": reason,
        "mode": "SHADOW",
        "response_modified": False,
        "runtime_authority_preserved": True,
    }
