from datetime import datetime, timezone
from typing import List, Dict, Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

PolicyMode = Literal["conservative", "balanced", "aggressive"]


class ModelUsage(BaseModel):
    model_name: str = Field(..., min_length=1, max_length=128)
    rpm_current: int = Field(..., ge=0, le=100000000)
    tpm_current: int = Field(..., ge=0, le=1000000000)
    error_rate: float = Field(..., ge=0.0, le=1.0, allow_inf_nan=False)
    latency_ms_avg: float = Field(..., ge=0.0, le=1000000000, allow_inf_nan=False)


class RateLimitRequest(BaseModel):
    policy: PolicyMode = "balanced"
    models: List[ModelUsage] = Field(..., max_length=1000)


class ModelRateLimitDecision(BaseModel):
    model_name: str
    rpm_limit: int
    tpm_limit: int
    status: str
    reason: str


class RateLimitResponse(BaseModel):
    policy: PolicyMode
    decisions: List[ModelRateLimitDecision]
    meta: Dict[str, Any]


def _policy_multiplier(policy: PolicyMode) -> float:
    if policy == "conservative":
        return 0.7
    if policy == "aggressive":
        return 1.3
    return 1.0


def _penalty_factor(error_rate: float, latency_ms: float) -> float:
    penalty = 1.0
    if error_rate > 0.1:
        penalty *= 0.7
    elif error_rate > 0.03:
        penalty *= 0.85

    if latency_ms > 800:
        penalty *= 0.7
    elif latency_ms > 400:
        penalty *= 0.9

    return penalty


def _status_from_factor(factor: float) -> str:
    if factor < 0.8:
        return "throttle"
    if factor > 1.1:
        return "expand"
    return "keep"


def _decide_for_model(policy: PolicyMode, usage: ModelUsage) -> ModelRateLimitDecision:
    base_mult = _policy_multiplier(policy)
    penalty = _penalty_factor(usage.error_rate, usage.latency_ms_avg)
    factor = base_mult * penalty

    # A zero observed usage is not evidence of a safe nonzero provider quota.
    # This endpoint emits planning hints only; it must never invent capacity.
    rpm_limit = max(0, int(usage.rpm_current * factor))
    tpm_limit = max(0, int(usage.tpm_current * factor))
    status = _status_from_factor(factor)
    if usage.rpm_current == 0 or usage.tpm_current == 0:
        status = 'throttle'
    reason = (
        f"policy={policy}, error_rate={usage.error_rate:.3f}, "
        f"latency_ms={usage.latency_ms_avg:.1f}, factor={factor:.2f}"
    )

    return ModelRateLimitDecision(
        model_name=usage.model_name,
        rpm_limit=rpm_limit,
        tpm_limit=tpm_limit,
        status=status,
        reason=reason,
    )


@router.post("/evaluate", response_model=RateLimitResponse)
def evaluate_rate_limits(request: RateLimitRequest) -> RateLimitResponse:
    if len({m.model_name for m in request.models}) != len(request.models):
        raise HTTPException(status_code=422, detail='duplicate model_name')
    decisions = [
        _decide_for_model(request.policy, m)
        for m in request.models
    ]
    return RateLimitResponse(
        policy=request.policy,
        decisions=decisions,
        meta={
            "version": "step443-v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "engine": "rate_limit_policy_step443",
        },
    )

