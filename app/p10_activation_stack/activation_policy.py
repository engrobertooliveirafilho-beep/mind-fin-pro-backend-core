import os
from dataclasses import dataclass

VALID_MODES = {"OFF", "DRY_RUN", "INTERNAL_ONLY", "LIMITED_ACTIVE", "ACTIVE"}

@dataclass(frozen=True)
class ActivationPolicy:
    enabled: bool
    mode: str
    may_modify_response: bool
    may_modify_runtime_state: bool
    may_modify_routes: bool
    may_modify_dispatcher: bool
    may_modify_whatsapp: bool
    rollback_required: bool

def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def _mode_env(name: str, default: str = "OFF") -> str:
    value = os.getenv(name, default).strip().upper()
    return value if value in VALID_MODES else "OFF"

def load_activation_policy() -> ActivationPolicy:
    mode = _mode_env("P10_ACTIVATION_MODE", "OFF")
    enabled = _bool_env("ENABLE_P10_CONTROLLED_ACTIVATION", False)

    may_modify_response = enabled and mode == "LIMITED_ACTIVE" and _bool_env("P10_ALLOW_RESPONSE_MODIFICATION", False)

    return ActivationPolicy(
        enabled=enabled,
        mode=mode,
        may_modify_response=may_modify_response,
        may_modify_runtime_state=False,
        may_modify_routes=False,
        may_modify_dispatcher=False,
        may_modify_whatsapp=False,
        rollback_required=True,
    )
