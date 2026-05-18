from __future__ import annotations
import os
from typing import Any
from app.runtime.runtime_registry import runtime_health_matrix

def whatsapp_intelligence_active() -> bool:
    return os.getenv("ELDORA_WHATSAPP_INTELLIGENCE_ACTIVE","0") == "1"

def enrich_whatsapp_context(user_id: str, message: str, base: dict | None = None) -> dict[str, Any]:
    base = dict(base or {})
    matrix = runtime_health_matrix()
    active = {k:v for k,v in matrix.items() if isinstance(v,dict) and v.get("status")=="operational"}
    base.update({
        "whatsapp_intelligence_active": whatsapp_intelligence_active(),
        "user_id": user_id,
        "message": message,
        "runtime_modules_active": sorted(active.keys()),
        "runtime_modules_count": len(active),
        "activation_mode": "controlled_feature_flag",
        "status": "operational"
    })
    return base
