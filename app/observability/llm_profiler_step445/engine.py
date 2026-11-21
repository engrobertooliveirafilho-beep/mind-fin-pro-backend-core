from datetime import datetime
from typing import List, Dict, Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

TuningHint = Literal["ok", "watch", "degrade"]


class LLMCallSample(BaseModel):
    model_name: str
    latency_ms: float = Field(..., ge=0.0)
    tokens_prompt: int = Field(..., ge=0)
    tokens_completion: int = Field(..., ge=0)
    success: bool = True


class ProfileRequest(BaseModel):
    window_id: str
    samples: List[LLMCallSample]


class ModelProfile(BaseModel):
    model_name: str
    calls: int
    success_rate: float
    avg_latency_ms: float
    max_latency_ms: float
    avg_tokens_total: float
    tuning_hint: TuningHint
    details: Dict[str, Any]


class ProfileResponse(BaseModel):
    window_id: str
    models: List[ModelProfile]
    meta: Dict[str, Any]


def _aggregate_for_model(model_name: str, samples: List[LLMCallSample]) -> ModelProfile:
    calls = len(samples)
    if calls == 0:
        return ModelProfile(
            model_name=model_name,
            calls=0,
            success_rate=1.0,
            avg_latency_ms=0.0,
            max_latency_ms=0.0,
            avg_tokens_total=0.0,
            tuning_hint="ok",
            details={},
        )

    successes = sum(1 for s in samples if s.success)
    success_rate = successes / calls
    latencies = [s.latency_ms for s in samples]
    avg_latency = sum(latencies) / calls
    max_latency = max(latencies)
    total_tokens = [s.tokens_prompt + s.tokens_completion for s in samples]
    avg_tokens = sum(total_tokens) / calls

    # Regras simples de hint
    if success_rate < 0.9 or max_latency > 1500:
        hint: TuningHint = "degrade"
    elif success_rate < 0.97 or avg_latency > 800:
        hint = "watch"
    else:
        hint = "ok"

    details = {
        "success_rate": round(success_rate, 4),
        "avg_latency_ms": round(avg_latency, 2),
        "max_latency_ms": round(max_latency, 2),
        "avg_tokens_total": round(avg_tokens, 2),
    }

    return ModelProfile(
        model_name=model_name,
        calls=calls,
        success_rate=round(success_rate, 4),
        avg_latency_ms=round(avg_latency, 2),
        max_latency_ms=round(max_latency, 2),
        avg_tokens_total=round(avg_tokens, 2),
        tuning_hint=hint,
        details=details,
    )


@router.post("/profile", response_model=ProfileResponse)
def profile_llm_usage(request: ProfileRequest) -> ProfileResponse:
    by_model: Dict[str, List[LLMCallSample]] = {}
    for s in request.samples:
        by_model.setdefault(s.model_name, []).append(s)

    profiles = [
        _aggregate_for_model(name, samples)
        for name, samples in by_model.items()
    ]

    return ProfileResponse(
        window_id=request.window_id,
        models=profiles,
        meta={
            "version": "step445-v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "llm_profiler_step445",
            "models_count": len(profiles),
        },
    )

