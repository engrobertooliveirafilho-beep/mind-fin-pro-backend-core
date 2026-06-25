
"""
P2397_META_LEARNING_OFFLINE

Offline-only meta-learning layer.
It creates research hypotheses.
It does not modify runtime routing.
It does not execute orders.
"""

from dataclasses import dataclass
from typing import Dict, Any, List

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

@dataclass(frozen=True)
class MetaLearningDecision:
    allowed_for_runtime: bool
    allowed_for_research: bool
    decision: str
    reason: str
    hypotheses: int
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL

class P2397MetaLearningOffline:
    def __init__(self, scored_edge: Dict[str, Any], hypotheses: List[Dict[str, Any]]):
        self.scored_edge = dict(scored_edge or {})
        self.hypotheses = list(hypotheses or [])

    def safety_check(self) -> bool:
        return MODE=="PAPER_ONLY" and REAL_ORDERS=="FORBIDDEN" and FTMO_REAL=="FORBIDDEN"

    def evaluate(self) -> MetaLearningDecision:
        if not self.safety_check():
            return MetaLearningDecision(False, False, "BLOCK", "SAFETY_LOCK_FAILED", 0)

        if self.scored_edge.get("decision") != "PROMOTE_SCORE":
            return MetaLearningDecision(
                allowed_for_runtime=False,
                allowed_for_research=True,
                decision="RESEARCH_ONLY",
                reason="EDGE_NOT_PROMOTED_META_LEARNING_OFFLINE_ONLY",
                hypotheses=len(self.hypotheses),
            )

        return MetaLearningDecision(
            allowed_for_runtime=False,
            allowed_for_research=True,
            decision="RESEARCH_ONLY",
            reason="META_LEARNING_NEVER_PROMOTES_DIRECTLY_TO_RUNTIME",
            hypotheses=len(self.hypotheses),
        )

def build_meta_learning(scored_edge: Dict[str, Any], hypotheses: List[Dict[str, Any]]):
    return P2397MetaLearningOffline(scored_edge, hypotheses)
