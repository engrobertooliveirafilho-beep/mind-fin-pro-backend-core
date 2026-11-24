from dataclasses import dataclass

@dataclass(frozen=True)
class EnsembleDecision:
    allowed: bool
    route: str
    confidence: float
    quorum: int
    votes: int
    reason: str
    mode: str = "PAPER_ONLY"
    real_orders: str = "FORBIDDEN"
    ftmo_real: str = "FORBIDDEN"

class P2406EdgeEnsembleOptimizer:
    def __init__(self, members, min_quorum=3, min_confidence=0.62):
        self.members = tuple(members or ())
        self.min_quorum = min_quorum
        self.min_confidence = min_confidence

    def vote(self, context):
        return EnsembleDecision(False, "BLOCK", 0.0, self.min_quorum, 0,
                                "P2405H_PROVENANCE_UNCERTIFIED")

def build_ensemble(members, min_quorum=3, min_confidence=0.62):
    return P2406EdgeEnsembleOptimizer(members, min_quorum, min_confidence)

def runtime_allowed():
    return False
