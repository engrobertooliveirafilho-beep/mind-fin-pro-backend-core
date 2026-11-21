from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class Metrics(BaseModel):
    cpu: float = Field(..., ge=0, le=100, allow_inf_nan=False)
    memory: float = Field(..., ge=0, le=100, allow_inf_nan=False)
    latency_ms: float = Field(..., ge=0, le=1000000000, allow_inf_nan=False)


class AutoscalingDecision(BaseModel):
    scale_horizontal: int
    scale_vertical: str
    rationale: str
    meta: Dict[str, Any]


def _decide_scale(metrics: Metrics) -> AutoscalingDecision:
    if metrics.cpu > 85 or metrics.latency_ms > 400:
        horiz = 2
        vert = "up"
        rationale = "CPU/latencia alta → expandir horizontal + vertical."
    elif metrics.cpu < 30 and metrics.memory < 30:
        horiz = -1
        vert = "down"
        rationale = "Uso baixo → reduzir recursos."
    else:
        horiz = 0
        vert = "keep"
        rationale = "Zona estável → manter estado atual."

    return AutoscalingDecision(
        scale_horizontal=horiz,
        scale_vertical=vert,
        rationale=rationale,
        meta={
            "version": "step441-v1",
            "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "engine": "autoscaling_policy_stub_step441",
        },
    )


@router.post("/recommend", response_model=AutoscalingDecision)
def recommend_scale(metrics: Metrics) -> AutoscalingDecision:
    return _decide_scale(metrics)

