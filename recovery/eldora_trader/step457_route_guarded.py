"""Recovered STEP457 GPU decision route with fail-closed zero-cost policy.
Isolated reconstruction; must be wired into the canonical app before E2E certification.
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.infra_gpu_autoscaling import compute_gpu_scaling_decision
from recovery.eldora_trader.step457_integration import guarded_decision

router = APIRouter()

class GpuAutoscalingDecisionRequest(BaseModel):
    queue_length: int = Field(..., ge=0)
    avg_latency_ms: float = Field(..., gt=0)
    current_instances: int = Field(..., ge=0)
    min_instances: int = Field(0, ge=0)
    max_instances: int = Field(32, ge=1)
    target_latency_ms: float = Field(1500.0, gt=0)
    cost_sensitivity: float = Field(1.0, gt=0)

@router.post('/infra/gpu-autoscaling/decision')
async def gpu_autoscaling_decision(req: GpuAutoscalingDecisionRequest):
    return guarded_decision(
        compute_gpu_scaling_decision,
        queue_length=req.queue_length, avg_latency_ms=req.avg_latency_ms,
        current_instances=req.current_instances, min_instances=req.min_instances,
        max_instances=req.max_instances, target_latency_ms=req.target_latency_ms,
        cost_sensitivity=req.cost_sensitivity, cost_limit_brl=0)
