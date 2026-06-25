import os
from dataclasses import dataclass

VALID_MODES = {"OFF", "SHADOW", "ACTIVE"}

@dataclass(frozen=True)
class P8FeatureFlags:
    enable_hierarchical_planner: bool
    enable_oversight: bool
    hierarchical_mode: str
    oversight_mode: str

def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def _mode_env(name: str, default: str = "OFF") -> str:
    value = os.getenv(name, default).strip().upper()
    return value if value in VALID_MODES else "OFF"

def load_p8_feature_flags() -> P8FeatureFlags:
    return P8FeatureFlags(
        enable_hierarchical_planner=_bool_env("ENABLE_HIERARCHICAL_PLANNER", False),
        enable_oversight=_bool_env("ENABLE_OVERSIGHT", False),
        hierarchical_mode=_mode_env("HIERARCHICAL_MODE", "OFF"),
        oversight_mode=_mode_env("OVERSIGHT_MODE", "OFF"),
    )
