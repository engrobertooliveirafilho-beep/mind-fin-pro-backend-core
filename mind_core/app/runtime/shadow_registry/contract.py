from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ShadowCapability:
    file: str
    action: str
    capability_score: int
    danger: List[str] = field(default_factory=list)
    route_like: bool = False
    functions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    enabled: bool = False
    production_allowed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


def is_shadow_only(capability: ShadowCapability) -> bool:
    return capability.enabled is True and capability.production_allowed is False
