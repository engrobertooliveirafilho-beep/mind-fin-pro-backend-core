"""P2396_EDGE_ENSEMBLE — unique, lineage-bound PAPER quorum."""
from dataclasses import asdict, dataclass
from collections.abc import Mapping
from math import isfinite
from typing import Any

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
    decision: str = "OBSERVE_ONLY"
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL
    real_execution_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class P2396EdgeEnsemble:
    def __init__(self, router_decisions: list[Mapping[str, Any]], quorum: int = 2):
        self.router_decisions = list(router_decisions) if isinstance(router_decisions, (list, tuple)) else []
        self.quorum = quorum
        self.mode = MODE
        self.real_orders = REAL_ORDERS
        self.ftmo_real = FTMO_REAL

    def safety_check(self) -> bool:
        return self.mode == MODE and self.real_orders == REAL_ORDERS and self.ftmo_real == FTMO_REAL

    @staticmethod
    def _valid_member(record: Any) -> bool:
        if not isinstance(record, Mapping):
            return False
        if (record.get("allowed") is not True
                or record.get("route") != "PAPER_SIGNAL_CANDIDATE"
                or record.get("decision") != "PAPER_ELIGIBLE"):
            return False
        if record.get("mode") != MODE or record.get("real_orders") != REAL_ORDERS:
            return False
        if record.get("ftmo_real") != FTMO_REAL or record.get("real_execution_allowed") is not False:
            return False
        if record.get("edge_status") != "PROMOTE_SCORE":
            return False
        if record.get("edge_score_decision") != "PROMOTE_SCORE":
            return False
        if not isinstance(record.get("source_cluster"), str) or not record["source_cluster"].strip():
            return False
        if not isinstance(record.get("source_edge"), str) or not record["source_edge"].strip():
            return False
        try:
            score = float(record.get("edge_score"))
        except (TypeError, ValueError):
            return False
        return isfinite(score)

    def vote(self) -> EnsembleVote:
        total = len(self.router_decisions)
        if not self.safety_check():
            return EnsembleVote(False, "BLOCK", "SAFETY_LOCK_FAILED", total, 0)
        if isinstance(self.quorum, bool) or not isinstance(self.quorum, int) or self.quorum < 1:
            return EnsembleVote(False, "BLOCK", "INVALID_QUORUM", total, 0)
        if not isinstance(self.router_decisions, list) or not self.router_decisions:
            return EnsembleVote(False, "OBSERVE_ONLY", "NO_ROUTER_MEMBERS", total, 0)

        accepted: dict[str, Mapping[str, Any]] = {}
        duplicate_ids: set[str] = set()
        for record in self.router_decisions:
            if not self._valid_member(record):
                continue
            source_edge = record["source_edge"]
            if source_edge in accepted:
                duplicate_ids.add(source_edge)
            else:
                accepted[source_edge] = record

        for duplicate_id in duplicate_ids:
            accepted.pop(duplicate_id, None)

        operational = len(accepted)
        if operational < self.quorum:
            return EnsembleVote(
                False, "OBSERVE_ONLY",
                "DUPLICATE_SOURCE_EDGE" if duplicate_ids else "INSUFFICIENT_OPERATIONAL_QUORUM",
                total, operational
            )

        return EnsembleVote(
            True, "PAPER_ELIGIBLE", "QUORUM_REACHED_PAPER_ONLY",
            total, operational, decision="PAPER_ELIGIBLE"
        )


def build_ensemble(router_decisions: list[Mapping[str, Any]], quorum: int = 2) -> P2396EdgeEnsemble:
    return P2396EdgeEnsemble(router_decisions, quorum=quorum)
