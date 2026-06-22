from datetime import datetime, timezone
from typing import Any, Dict

VERSION = "P19P37B_BEHAVIOR_MODELING"

def infer_behavior_model(ctx: Dict[str, Any] | None = None, text: str = "", sender: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    lower = str(text or "").lower()

    behavior = {
        "sender": sender,
        "urgency": "LOW",
        "execution_style": "UNKNOWN",
        "planning_depth": "UNKNOWN",
        "risk_tolerance": "UNKNOWN",
        "preferred_format": "UNKNOWN",
        "signals": [],
        "mode": "SHADOW_ONLY",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "version": VERSION,
    }

    if any(x in lower for x in ["prossiga", "executar", "powershell", "comando"]):
        behavior["execution_style"] = "ACTION_ORIENTED"
        behavior["preferred_format"] = "POWERSHELL"
        behavior["signals"].append("action_oriented")

    if any(x in lower for x in ["auditoria", "evidência", "snapshot", "rollback"]):
        behavior["planning_depth"] = "AUDIT_DRIVEN"
        behavior["signals"].append("audit_driven")

    if any(x in lower for x in ["rápido", "menor caminho", "máximo"]):
        behavior["urgency"] = "HIGH"
        behavior["signals"].append("speed_priority")

    if any(x in lower for x in ["seguro", "sem quebrar", "rollback"]):
        behavior["risk_tolerance"] = "CONTROLLED"
        behavior["signals"].append("safety_controlled")

    return behavior

def attach_behavior_model_shadow(ctx: Dict[str, Any] | None = None, sender: str = "", text: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p37b_behavior_model_shadow"] = infer_behavior_model(ctx, text=text, sender=sender)
    return ctx
