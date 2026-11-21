from datetime import datetime
from typing import List, Dict, Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

Modality = Literal["text", "audio", "video", "three_d"]


class MultimodalChannel(BaseModel):
    channel_id: str
    modality: Modality
    size_bytes: int = Field(..., ge=0)
    priority: int = Field(5, ge=1, le=10)


class MultimodalExecuteRequest(BaseModel):
    session_id: str
    channels: List[MultimodalChannel]


class ChannelRoute(BaseModel):
    channel_id: str
    modality: Modality
    pipeline: str
    estimated_tokens: int
    latency_class: str
    priority: int
    reason: str


class MultimodalExecuteResponse(BaseModel):
    session_id: str
    routes: List[ChannelRoute]
    stats: Dict[str, Any]
    meta: Dict[str, Any]


def _pipeline_for_modality(modality: Modality) -> str:
    if modality == "text":
        return "nlp_core"
    if modality == "audio":
        return "audio_asr"
    if modality == "video":
        return "video_vision"
    return "three_d_engine"


def _latency_class_for_modality(modality: Modality) -> str:
    if modality == "text":
        return "low"
    if modality == "audio":
        return "medium"
    if modality == "video":
        return "high"
    return "high"


def _estimate_tokens(size_bytes: int, modality: Modality) -> int:
    if modality == "text":
        return max(1, size_bytes // 4)
    if modality == "audio":
        return max(50, size_bytes // 200)
    if modality == "video":
        return max(200, size_bytes // 500)
    # three_d
    return max(300, size_bytes // 800)


@router.post("/execute", response_model=MultimodalExecuteResponse)
def execute_multimodal(request: MultimodalExecuteRequest) -> MultimodalExecuteResponse:
    routes: List[ChannelRoute] = []

    for ch in request.channels:
        pipeline = _pipeline_for_modality(ch.modality)
        latency_class = _latency_class_for_modality(ch.modality)
        est_tokens = _estimate_tokens(ch.size_bytes, ch.modality)
        reason = f"modality={ch.modality}, pipeline={pipeline}, priority={ch.priority}"

        routes.append(
            ChannelRoute(
                channel_id=ch.channel_id,
                modality=ch.modality,
                pipeline=pipeline,
                estimated_tokens=est_tokens,
                latency_class=latency_class,
                priority=ch.priority,
                reason=reason,
            )
        )

    stats = {
        "channels": len(request.channels),
        "modalities": sorted({ch.modality for ch in request.channels}),
        "total_estimated_tokens": sum(r.estimated_tokens for r in routes),
    }

    return MultimodalExecuteResponse(
        session_id=request.session_id,
        routes=routes,
        stats=stats,
        meta={
            "version": "step456-v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "multimodal_executor_step456",
        },
    )

