
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
        self.quorum = quorum
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

        if type(self.quorum) is not int or self.quorum < 2:
            return EnsembleVote(False, "BLOCK", "INVALID_QUORUM", len(self.router_decisions), 0)
        seen = set()
        operational = []
        for r in self.router_decisions:
            if not isinstance(r, dict):
                return EnsembleVote(False, "BLOCK", "INVALID_ROUTER_DECISION", len(self.router_decisions), 0)
            member_id = r.get("member_id")
            if not isinstance(member_id, str) or not member_id.strip():
                return EnsembleVote(False, "BLOCK", "MEMBER_ID_REQUIRED", len(self.router_decisions), 0)
            if member_id in seen:
                return EnsembleVote(False, "BLOCK", "DUPLICATE_MEMBER", len(self.router_decisions), 0)
            seen.add(member_id)
            if r.get("mode") != MODE or r.get("real_orders") != REAL_ORDERS or r.get("ftmo_real") != FTMO_REAL:
                return EnsembleVote(False, "BLOCK", "UNSAFE_ROUTER_DECISION", len(self.router_decisions), 0)
            if r.get("allowed") is True and r.get("route") == "PAPER_SIGNAL_CANDIDATE":
                operational.append(r)

        if len(operational) < self.quorum:
            return EnsembleVote(
                allowed=False,
                vote="OBSERVE_ONLY",
                reason="INSUFFICIENT_OPERATIONAL_QUORUM",
                members=len(self.router_decisions),
                operational_members=len(operational),
            )

        return EnsembleVote(
            allowed=False,
            vote="BLOCK",
            reason="INDEPENDENT_ENSEMBLE_EVIDENCE_REQUIRED",
            members=len(self.router_decisions),
            operational_members=len(operational),
        )


def build_ensemble(router_decisions: List[Dict[str, Any]], quorum: int = 2) -> P2396EdgeEnsemble:
    return P2396EdgeEnsemble(router_decisions, quorum=quorum)
