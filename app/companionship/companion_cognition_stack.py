from datetime import datetime, timezone
from typing import Any, Dict

VERSION = "07_P19P36U_COMPANION_COGNITION_STACK"

def build_shadow(ctx: Dict[str, Any] | None = None, text: str = "", sender: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    lower = str(text or "").lower()
    signals = []
    if "dor" in lower: signals.append("pain_signal")
    if "frustr" in lower or "trav" in lower: signals.append("friction_signal")
    if "quero" in lower or "meta" in lower: signals.append("goal_signal")
    return {
        "sender": sender,
        "signals": signals,
        "source_keys": sorted(list(ctx.keys()))[:30],
        "mode": "SHADOW_ONLY",
        "response_impact": "NONE",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "version": VERSION,
    }

def attach_shadow(ctx: Dict[str, Any] | None = None, sender: str = "", text: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p36u_companion_cognition_shadow"] = build_shadow(ctx, text=text, sender=sender)
    return ctx
