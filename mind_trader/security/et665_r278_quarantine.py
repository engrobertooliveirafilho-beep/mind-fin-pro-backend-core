"""ET665.R278 fail-closed quarantine for unverified P2401 lineage. Research only."""
from dataclasses import dataclass
from typing import Mapping, Any

QUARANTINED = frozenset(("P2401", "P2402", "P2403", "P2404", "P2405H", "P2406", "P2407", "P2408"))

@dataclass(frozen=True)
class Decision:
    allowed: bool
    status: str
    reason: str
    mode: str = "PAPER_ONLY"
    real_orders: str = "FORBIDDEN"
    ftmo_real: str = "FORBIDDEN"

def evaluate(candidate: Mapping[str, Any], evidence: Mapping[str, Any] | None = None) -> Decision:
    if not isinstance(candidate, Mapping):
        return Decision(False, "BLOCK", "INVALID_CANDIDATE")
    if candidate.get("mode") != "PAPER_ONLY" or candidate.get("real_orders") != "FORBIDDEN" or candidate.get("ftmo_real") != "FORBIDDEN" or candidate.get("real_execution_allowed") is not False:
        return Decision(False, "BLOCK", "SAFETY_CONTRACT_FAILED")
    lineage = candidate.get("lineage")
    if not isinstance(lineage, (list, tuple)) or not lineage or any(not isinstance(x, str) for x in lineage):
        return Decision(False, "OBSERVE_ONLY", "UNVERIFIED_LINEAGE")
    if any(any(x.startswith(prefix) for prefix in QUARANTINED) for x in lineage):
        return Decision(False, "QUARANTINE", "SYNTHETIC_OR_UNVERIFIED_WALK_FORWARD_LINEAGE")
    return Decision(False, "OBSERVE_ONLY", "CAUSAL_AND_P2389_CERTIFICATION_REQUIRED")
