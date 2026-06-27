from dataclasses import dataclass, asdict
from typing import Dict, Any

from app.runtime.final_authority_divergence_analyzer import analyze_canary_diff


@dataclass
class PromotionGateDecision:
    approved: bool
    reason: str
    metrics: Dict[str, Any]
    required: Dict[str, Any]
    mode: str = "PROMOTION_GATE_ONLY"


def evaluate_final_authority_promotion(
    canary_log_path: str,
    *,
    min_samples: int = 10,
    min_equivalence_rate: float = 0.98,
    max_error_rate: float = 0.0,
    max_critical_divergences: int = 0,
) -> PromotionGateDecision:
    result = analyze_canary_diff(canary_log_path)

    required = {
        "min_samples": min_samples,
        "min_equivalence_rate": min_equivalence_rate,
        "max_error_rate": max_error_rate,
        "max_critical_divergences": max_critical_divergences,
    }

    total = int(result.get("total", 0) or 0)
    equivalence_rate = float(result.get("equivalence_rate", 0.0) or 0.0)
    error_rate = float(result.get("error_rate", 1.0) if result.get("error_rate", None) is not None else 1.0)
    critical = int(result.get("severity_count", {}).get("CRITICAL", 0) or 0)

    metrics = {
        "ok": result.get("ok") is True,
        "total": total,
        "equivalence_rate": equivalence_rate,
        "error_rate": error_rate,
        "critical_divergences": critical,
        "promotion_ready_from_analyzer": result.get("promotion_ready") is True,
    }

    if result.get("ok") is not True:
        return PromotionGateDecision(False, "ANALYZER_NOT_OK", metrics, required)

    if total < min_samples:
        return PromotionGateDecision(False, "INSUFFICIENT_SAMPLES", metrics, required)

    if equivalence_rate < min_equivalence_rate:
        return PromotionGateDecision(False, "EQUIVALENCE_RATE_TOO_LOW", metrics, required)

    if error_rate > max_error_rate:
        return PromotionGateDecision(False, "ERROR_RATE_TOO_HIGH", metrics, required)

    if critical > max_critical_divergences:
        return PromotionGateDecision(False, "CRITICAL_DIVERGENCES_PRESENT", metrics, required)

    return PromotionGateDecision(True, "PROMOTION_APPROVED_FOR_CONTROLLED_CANARY", metrics, required)


def promotion_gate_to_dict(decision: PromotionGateDecision) -> Dict[str, Any]:
    return asdict(decision)
