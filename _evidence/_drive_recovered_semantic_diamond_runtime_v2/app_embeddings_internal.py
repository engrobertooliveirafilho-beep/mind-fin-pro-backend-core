from __future__ import annotations
from typing import List, Dict, Any
import hashlib
import math
import time


DEFAULT_INTERNAL_MODEL = "mind-embed-internal-1"


def _text_to_vec(text: str, dim: int = 16) -> List[float]:
    if not text:
        return [0.0] * dim
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vals: List[float] = []
    for i in range(dim):
        b1 = h[(2 * i) % len(h)]
        b2 = h[(2 * i + 1) % len(h)]
        raw = (b1 << 8) | b2
        signed = raw - 65536 if raw >= 32768 else raw
        vals.append(signed / 32768.0)
    norm = math.sqrt(sum(v * v for v in vals)) or 1.0
    return [v / norm for v in vals]


def embed_text_internal(text: str, model: str | None = None) -> Dict[str, Any]:
    m = model or DEFAULT_INTERNAL_MODEL
    vec = _text_to_vec(text or "")
    return {
        "model": m,
        "provider": "internal_hash_stub",
        "vector": vec,
        "dim": len(vec),
        "created_at": time.time(),
    }


def embed_batch_internal(texts: List[str], model: str | None = None) -> Dict[str, Any]:
    m = model or DEFAULT_INTERNAL_MODEL
    items: List[Dict[str, Any]] = []
    for idx, t in enumerate(texts or []):
        items.append(
            {
                "index": idx,
                "text": t,
                "embedding": _text_to_vec(t or ""),
            }
        )
    return {
        "model": m,
        "provider": "internal_hash_stub",
        "items": items,
        "count": len(items),
        "created_at": time.time(),
    }
