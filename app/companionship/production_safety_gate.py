import os

VERSION="P19P36Y_PRODUCTION_SAFETY_GATE"

def production_cognition_enabled() -> bool:
    return str(os.getenv("P19P36_ENABLE_PRODUCTION_COGNITION", "false")).lower() in {"1","true","yes","on"}

def evaluate_production_safety(ctx=None):
    return {
        "enabled": production_cognition_enabled(),
        "default_safe": not production_cognition_enabled(),
        "mode": "BLOCKED_BY_DEFAULT" if not production_cognition_enabled() else "EXPLICITLY_ENABLED",
        "version": VERSION,
    }
