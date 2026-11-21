from datetime import datetime
from typing import List, Dict, Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class RegionConfig(BaseModel):
    name: str
    base_latency_ms: float = Field(..., ge=0)
    write_capacity_rps: float = Field(..., gt=0)


class ReplicationPlanRequest(BaseModel):
    regions: List[RegionConfig]
    global_write_rate_rps: float = Field(..., gt=0)
    consistency_mode: Literal["strong", "eventual"] = "eventual"


class RegionPlan(BaseModel):
    name: str
    assigned_write_rps: float
    estimated_replication_lag_ms: float
    conflict_risk: str


class ReplicationPlanResponse(BaseModel):
    regions: List[RegionPlan]
    notes: List[str]
    meta: Dict[str, Any]


def _classify_conflict_risk(write_ratio: float, latency_ms: float, consistency_mode: str) -> str:
    score = write_ratio * (latency_ms / 100.0)
    if consistency_mode == "strong":
        score *= 1.5
    if score < 0.5:
        return "low"
    if score < 1.5:
        return "medium"
    return "high"


def _estimate_lag(base_latency_ms: float, load_factor: float, consistency_mode: str) -> float:
    factor = 1.0 + load_factor
    if consistency_mode == "strong":
        factor *= 1.3
    return base_latency_ms * factor


@router.post("/plan", response_model=ReplicationPlanResponse)
def plan_replication(request: ReplicationPlanRequest) -> ReplicationPlanResponse:
    total_capacity = sum(r.write_capacity_rps for r in request.regions)
    if total_capacity <= 0:
        raise ValueError("Total capacity must be positive.")

    regions_plan: List[RegionPlan] = []

    for region in request.regions:
        cap_ratio = region.write_capacity_rps / total_capacity
        assigned_write = cap_ratio * request.global_write_rate_rps
        load_factor = assigned_write / region.write_capacity_rps
        lag = _estimate_lag(region.base_latency_ms, load_factor, request.consistency_mode)
        risk = _classify_conflict_risk(
            write_ratio=assigned_write / request.global_write_rate_rps,
            latency_ms=lag,
            consistency_mode=request.consistency_mode,
        )

        regions_plan.append(
            RegionPlan(
                name=region.name,
                assigned_write_rps=round(assigned_write, 2),
                estimated_replication_lag_ms=round(lag, 2),
                conflict_risk=risk,
            )
        )

    notes = [
        f"consistency_mode={request.consistency_mode}",
        "modelo puramente simulado (nenhuma infra real afetada)",
    ]

    return ReplicationPlanResponse(
        regions=regions_plan,
        notes=notes,
        meta={
            "version": "step442-v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "replication_planner_stub_step442",
        },
    )

