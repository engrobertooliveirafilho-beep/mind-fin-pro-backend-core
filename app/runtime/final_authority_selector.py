from __future__ import annotations

from typing import Any, Dict, List


GENERIC_MARKERS = [
    "context_signal",
    "entendi. vou seguir pelo contexto",
    "vamos fazer direito",
    "primeiro eu preciso dos seus dados",
]


def _text(candidate: Dict[str, Any]) -> str:
    value = candidate.get("text", "")
    return str(value or "").strip()


def _is_generic(text: str) -> bool:
    low = str(text or "").lower()
    return any(marker in low for marker in GENERIC_MARKERS)


def _score_candidate(candidate: Dict[str, Any]) -> int:
    text = _text(candidate)
    source = str(candidate.get("source", "unknown"))
    safe = candidate.get("safe") is True
    send_to_user = candidate.get("send_to_user") is True

    score = 0

    if safe:
        score += 30

    if text:
        score += 20

    if len(text) >= 40:
        score += 10

    if not _is_generic(text):
        score += 20
    else:
        score -= 50

    if source == "universal_authority_renderer":
        score += 10

    if source == "cognitive_pipeline":
        score += 15

    if source == "legacy_context_signal":
        score -= 30

    if send_to_user:
        score += 5

    return score


def select_final_authority_candidate(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Selects the safest best candidate.
    Does not execute capabilities.
    Does not authorize production.
    Does not force send_to_user.
    """
    result: Dict[str, Any] = {
        "mode": "FINAL_AUTHORITY_SELECTOR",
        "ok": False,
        "send_to_user": False,
        "selected": None,
        "selected_index": None,
        "score": None,
        "reason": "",
        "ranked": [],
    }

    if not isinstance(candidates, list):
        result["reason"] = "candidates_not_list"
        return result

    ranked = []
    for idx, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            continue

        score = _score_candidate(candidate)
        ranked.append({
            "index": idx,
            "score": score,
            "source": candidate.get("source", "unknown"),
            "safe": candidate.get("safe"),
            "send_to_user": candidate.get("send_to_user"),
            "text_preview": _text(candidate)[:200],
            "generic": _is_generic(_text(candidate)),
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    result["ranked"] = ranked

    if not ranked:
        result["reason"] = "no_valid_candidates"
        return result

    best = ranked[0]
    selected = candidates[best["index"]]

    result["ok"] = True
    result["selected"] = selected
    result["selected_index"] = best["index"]
    result["score"] = best["score"]
    result["send_to_user"] = selected.get("send_to_user") is True
    result["reason"] = "selected_highest_safe_score"

    return result
