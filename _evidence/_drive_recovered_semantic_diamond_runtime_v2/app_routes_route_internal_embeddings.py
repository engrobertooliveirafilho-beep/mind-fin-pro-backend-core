from typing import List, Dict, Any
import hashlib
import json

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter()


class InternalEmbeddingRequest(BaseModel):
    text: str = Field(..., description="Texto para embedding interno")
    namespace: str = Field(..., description="Namespace lógico para o índice interno")
    dim: int = Field(..., gt=0, le=4096, description="Dimensão desejada do vetor")


def _deterministic_embedding_01(text: str, namespace: str, dim: int) -> List[float]:
    """
    Gera um embedding determinístico em [0, 1].
    - len == dim
    - cada valor 0.0 <= v <= 1.0
    - determinístico para (text, namespace, dim)
    """
    vec: List[float] = []
    for i in range(dim):
        seed = f"{text}|{namespace}|{i}".encode("utf-8")
        h = hashlib.sha256(seed).digest()
        # pega 8 bytes como inteiro
        v_int = int.from_bytes(h[:8], byteorder="big", signed=False)
        # mapeia pra [0,1)
        v = (v_int % 1_000_000) / 1_000_000.0
        vec.append(v)
    return vec


def _checksum_vector(vec: List[float]) -> str:
    """
    Checksum determinístico do vetor usando SHA-256 sobre o JSON do vetor.
    """
    payload = json.dumps(vec, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@router.post("/ai/embeddings/internal/embed")
def internal_embeddings_embed(payload: InternalEmbeddingRequest) -> Dict[str, Any]:
    """
    STEP454 – Embeddings internos determinísticos em [0,1] com checksum estável.
    """
    dim = max(1, payload.dim)
    vector = _deterministic_embedding_01(payload.text, payload.namespace, dim)

    sq_sum = sum(x * x for x in vector)
    norm = sq_sum ** 0.5
    checksum = _checksum_vector(vector)

    result = {
        "text": payload.text,
        "namespace": payload.namespace,
        "dim": dim,
        "vector": vector,
        "embedding": vector,  # alias
        "norm": norm,
        "checksum": checksum,
    }

    return {
        "text": payload.text,
        "namespace": payload.namespace,
        "dim": dim,
        "vector": vector,
        "embedding": vector,
        "checksum": checksum,
        "result": result,
        "meta": {"engine": "internal-embeddings", "version": "step454-v1"},
    }
