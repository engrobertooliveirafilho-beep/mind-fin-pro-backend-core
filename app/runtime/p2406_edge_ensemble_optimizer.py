
from dataclasses import dataclass
from typing import List, Dict, Any

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

@dataclass(frozen=True)
class EnsembleDecision:
    allowed: bool
    route: str
    confidence: float
    quorum: int
    votes: int
    reason: str
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL

class P2406EdgeEnsembleOptimizer:
    def __init__(self, members: List[Dict[str, Any]], min_quorum: int = 3, min_confidence: float = 0.62):
        self.members = list(members or [])
        self.min_quorum = int(min_quorum)
        self.min_confidence = float(min_confidence)

    def safety_check(self):
        return MODE=="PAPER_ONLY" and REAL_ORDERS=="FORBIDDEN" and FTMO_REAL=="FORBIDDEN"

    def vote(self, context: Dict[str, Any]) -> EnsembleDecision:
        if not self.safety_check():
            return EnsembleDecision(False,"BLOCK",0.0, self.min_quorum,0,"SAFETY_LOCK_FAILED")

        active=[m for m in self.members if m.get("status","ENSEMBLE_MEMBER")=="ENSEMBLE_MEMBER"]
        votes=len(active)
        if votes < self.min_quorum:
            return EnsembleDecision(False,"OBSERVE_ONLY",0.0,self.min_quorum,votes,"QUORUM_NOT_REACHED")

        total_weight=sum(float(m.get("ensemble_weight",0)) for m in active)
        confidence=min(1.0,total_weight)

        if confidence < self.min_confidence:
            return EnsembleDecision(False,"OBSERVE_ONLY",confidence,self.min_quorum,votes,"CONFIDENCE_BELOW_GATE")

        return EnsembleDecision(True,"PAPER_SIGNAL_CANDIDATE",confidence,self.min_quorum,votes,"ENSEMBLE_APPROVED_PAPER_ONLY")

def build_ensemble(members, min_quorum=3, min_confidence=0.62):
    return P2406EdgeEnsembleOptimizer(members, min_quorum, min_confidence)

def runtime_allowed():
    return False
