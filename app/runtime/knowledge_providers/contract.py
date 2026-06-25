from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class KnowledgePacket:
    domain: str
    intent: str
    facts: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def packet_to_context(packet: KnowledgePacket) -> str:
    parts = [
        f"domain={packet.domain}",
        f"intent={packet.intent}",
        "facts=" + "; ".join(packet.facts),
        "constraints=" + "; ".join(packet.constraints),
        "steps=" + "; ".join(packet.steps),
        "priorities=" + "; ".join(packet.priorities),
        "warnings=" + "; ".join(packet.warnings),
        f"source={packet.source}",
    ]
    return "\n".join([p for p in parts if p and not p.endswith("=")])
