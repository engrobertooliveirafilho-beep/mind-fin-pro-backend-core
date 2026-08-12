from __future__ import annotations

def is_state_query(text: str) -> bool:
    t=(text or "").lower()
    return any(x in t for x in [
        "estado atual",
        "resuma o estado",
        "onde estamos",
        "status atual",
        "snapshot",
        "baseline"
    ])

def build_mind_state_visible_response() -> str:
    # GATE1F: meta-runtime user-facing generator disabled
    return None
