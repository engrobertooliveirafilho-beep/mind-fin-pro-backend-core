import os
from dataclasses import dataclass

VALID_MODES = {"OFF", "DRY_RUN", "INTERNAL", "ACTIVE"}

@dataclass(frozen=True)
class RuntimeConsumptionGate:
    enabled: bool
    mode: str
    may_modify_response: bool
    may_modify_runtime_state: bool
    may_modify_routes: bool
    may_modify_dispatcher: bool
    may_call_external_tools: bool

def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def _mode_env(name: str, default: str = "OFF") -> str:
    value = os.getenv(name, default).strip().upper()
    return value if value in VALID_MODES else "OFF"

def load_runtime_consumption_gate() -> RuntimeConsumptionGate:
    mode = _mode_env("P9_RUNTIME_CONSUMPTION_MODE", "OFF")
    enabled = _bool_env("ENABLE_P9_RUNTIME_CONSUMPTION", False)

    return RuntimeConsumptionGate(
        enabled=enabled,
        mode=mode,
        may_modify_response=False,
        may_modify_runtime_state=False,
        may_modify_routes=False,
        may_modify_dispatcher=False,
        may_call_external_tools=False,
    )
