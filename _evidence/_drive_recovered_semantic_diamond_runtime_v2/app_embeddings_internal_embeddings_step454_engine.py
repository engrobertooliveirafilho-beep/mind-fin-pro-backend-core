from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class EmbedRequest(BaseModel):
    text: str
    namespace: str = "default"
    dim: int = Field(32, ge=8, le=256)


class EmbedResponse(BaseModel):
    namespace: str
    dim: int
    vector: List[float]
    checksum: int
    meta: Dict[str, Any]


def _hash_text(text: str) -> int:
    # Hash simples, deterministico, sem usar libs externas
    h = 0
    for ch in text:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return h


def _build_embedding(text: str, dim: int) -> List[float]:
    base_hash = _hash_text(text)
    if dim <= 0:
        dim = 32
    vec: List[float] = []
    for i in range(dim):
        # Gera pseudo-randomico deterministico a partir do hash base
        val = (base_hash ^ (i * 2654435761 & 0xFFFFFFFF)) & 0xFFFFFFFF
        # Normaliza para [0,1]
        vec.append(val / 4294967295.0)
    return vec


@router.post("/embed", response_model=EmbedResponse)
def embed_internal(request: EmbedRequest) -> EmbedResponse:
    vector = _build_embedding(request.text, request.dim)
    checksum = _hash_text(request.text + "|" + request.namespace)

    return EmbedResponse(
        namespace=request.namespace,
        dim=len(vector),
        vector=vector,
        checksum=checksum,
        meta={
            "version": "step454-v1",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "engine": "internal_embeddings_step454",
        },
    )
