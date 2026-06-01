from datetime import datetime
from math import ceil
from typing import Dict, Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()

CompressionMode = Literal["none", "fp16", "int8"]


class VectorIndexPlanRequest(BaseModel):
    total_vectors: int = Field(..., gt=0)
    dim: int = Field(32, ge=8, le=4096)
    max_shard_size: int = Field(1_000_000, gt=0)
    page_size: int = Field(10_000, gt=0)
    compression: CompressionMode = "fp16"


class ShardLayout(BaseModel):
    shard_id: int
    vectors_in_shard: int
    pages: int
    approx_bytes_mb: float


class VectorIndexPlanResponse(BaseModel):
    total_vectors: int
    dim: int
    shards_count: int
    compression: CompressionMode
    total_bytes_mb: float
    layout: Dict[str, ShardLayout]
    meta: Dict[str, Any]


def _compression_factor(mode: CompressionMode) -> float:
    if mode == "none":
        return 1.0  # 4 bytes/float32
    if mode == "fp16":
        return 0.5  # 2 bytes
    return 0.25  # int8 ~1 byte


def _estimate_bytes_mb(vectors: int, dim: int, mode: CompressionMode) -> float:
    bytes_per_vec = dim * 4 * _compression_factor(mode)
    total_bytes = vectors * bytes_per_vec
    return total_bytes / (1024.0 * 1024.0)


@router.post("/plan", response_model=VectorIndexPlanResponse)
def plan_vector_index(request: VectorIndexPlanRequest) -> VectorIndexPlanResponse:
    shards_count = ceil(request.total_vectors / request.max_shard_size)
    layout: Dict[str, ShardLayout] = {}
    remaining = request.total_vectors
    total_bytes = 0.0

    for shard_id in range(1, shards_count + 1):
        capacity = request.max_shard_size
        vectors_here = capacity if remaining > capacity else remaining
        remaining -= vectors_here
        pages = ceil(vectors_here / request.page_size)
        mb = _estimate_bytes_mb(vectors_here, request.dim, request.compression)
        total_bytes += mb

        layout[str(shard_id)] = ShardLayout(
            shard_id=shard_id,
            vectors_in_shard=vectors_here,
            pages=pages,
            approx_bytes_mb=round(mb, 3),
        )

    return VectorIndexPlanResponse(
        total_vectors=request.total_vectors,
        dim=request.dim,
        shards_count=shards_count,
        compression=request.compression,
        total_bytes_mb=round(total_bytes, 3),
        layout=layout,
        meta={
            "version": "step455-v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "vector_index_step455_planner",
        },
    )
