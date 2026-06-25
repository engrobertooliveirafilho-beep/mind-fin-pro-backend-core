
"""
P2396_EDGE_ENSEMBLE
Defensive PAPER_ONLY ensemble layer.

This module does not execute orders.
It only evaluates whether enough certified scored/router-approved edges exist.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


@dataclass(frozen=True)
class EnsembleVote:
    allowed: bool
    vote: str
    reason: str
    members: int
    operational_members: int
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL


class P2396EdgeEnsemble:
    def __init__(self, router_decisions: List[Dict[str, Any]], quorum: int = 2):
        self.router_decisions = list(router_decisions or [])
        self.quorum = int(quorum)
        self.mode = MODE
        self.real_orders = REAL_ORDERS
        self.ftmo_real = FTMO_REAL

    def safety_check(self) -> bool:
        return (
            self.mode == "PAPER_ONLY"
            and self.real_orders == "FORBIDDEN"
            and self.ftmo_real == "FORBIDDEN"
        )

    def vote(self) -> EnsembleVote:
        if not self.safety_check():
            return EnsembleVote(False, "BLOCK", "SAFETY_LOCK_FAILED", len(self.router_decisions), 0)

        operational = [
            r for r in self.router_decisions
            if r.get("allowed") is True and r.get("route") == "PAPER_SIGNAL_CANDIDATE"
        ]

        if len(operational) < self.quorum:
            return EnsembleVote(
                allowed=False,
                vote="OBSERVE_ONLY",
                reason="INSUFFICIENT_OPERATIONAL_QUORUM",
                members=len(self.router_decisions),
                operational_members=len(operational),
            )

        return EnsembleVote(
            allowed=True,
            vote="PAPER_CONSENSUS_CANDIDATE",
            reason="QUORUM_REACHED_PAPER_ONLY",
            members=len(self.router_decisions),
            operational_members=len(operational),
        )


def build_ensemble(router_decisions: List[Dict[str, Any]], quorum: int = 2) -> P2396EdgeEnsemble:
    return P2396EdgeEnsemble(router_decisions, quorum=quorum)
