
import re
from typing import Any

_STOP = {
    "o","a","os","as","de","do","da","dos","das","e","ou","um","uma",
    "meu","minha","qual","que","quem","como","para","pra","por","com",
    "eu","voce","você","estou","esta","está"
}

def _tokens(text: str) -> set[str]:
    return {
        t for t in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", (text or "").lower())
        if len(t) > 2 and t not in _STOP
    }

def rerank_memories(query: str, memories: list[Any], limit: int = 3) -> list[Any]:
    qtok = _tokens(query)
    ranked = []
    seen = set()

    for idx, item in enumerate(memories or []):
        if isinstance(item, dict):
            msg = str(item.get("message") or item.get("text") or "")
            base_score = float(item.get("score") or 0.0)
        else:
            msg = str(item)
            base_score = 0.0

        norm = " ".join(msg.lower().split())
        if not norm or norm in seen:
            continue
        seen.add(norm)

        mtok = _tokens(msg)
        lexical = len(qtok & mtok)
        density = lexical / max(1, len(qtok))
        recency_bias = max(0.0, 1.0 - (idx * 0.05))
        specificity = min(1.0, len(mtok) / 12.0)

        final_score = (density * 3.0) + (base_score * 1.0) + (specificity * 0.4) + (recency_bias * 0.2)

        if isinstance(item, dict):
            enriched = dict(item)
            enriched["rerank_score"] = final_score
            enriched["rerank_reason"] = {
                "lexical_overlap": lexical,
                "density": round(density, 4),
                "base_score": base_score,
                "specificity": round(specificity, 4)
            }
        else:
            enriched = {
                "message": msg,
                "score": base_score,
                "rerank_score": final_score,
                "rerank_reason": {
                    "lexical_overlap": lexical,
                    "density": round(density, 4),
                    "base_score": base_score,
                    "specificity": round(specificity, 4)
                }
            }

        ranked.append(enriched)

    ranked.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
    return ranked[:limit]


def contextual_rerank(query: str, rows: list, limit: int = 3):
    """
    Backward compatibility shim.
    Old runtime imports contextual_rerank().
    """
    return rerank_memories(query, rows, limit)
