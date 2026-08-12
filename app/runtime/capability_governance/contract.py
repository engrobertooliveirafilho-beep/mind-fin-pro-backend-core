from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class CapabilityDescriptor:
    id: str
    name: str
    path: str
    domains: List[str] = field(default_factory=list)
    intents: List[str] = field(default_factory=list)
    mode: str = "shadow"
    priority: int = 0
    confidence: float = 0.0
    health: str = "unknown"
    produces: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)

@dataclass
class GovernanceRequest:
    text: str
    domain: Optional[str] = None
    intent: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GovernanceDecision:
    selected: List[CapabilityDescriptor]
    rejected: List[Dict[str, Any]]
    reason: str
    mode: str = "shadow"
    final_authority: str = "capability_governance_engine"
