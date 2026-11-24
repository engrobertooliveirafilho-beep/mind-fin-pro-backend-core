"""P2395_CONTEXT_ROUTER_V2 — fail-closed PAPER context validation."""
from dataclasses import asdict, dataclass
from math import isfinite
from collections.abc import Mapping
from typing import Any

MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


@dataclass(frozen=True)
class ContextRouteDecision:
    allowed: bool
    route: str
    reason: str
    edge_status: str
    decision: str = "OBSERVE_ONLY"
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL
    real_execution_allowed: bool = False
    source_cluster: str = ""
    source_edge: str = ""
    edge_score: float = 0.0
    edge_score_decision: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class P2395ContextRouterV2:
    def __init__(self, scored_edge: Mapping[str, Any]):
        self.scored_edge = dict(scored_edge) if isinstance(scored_edge, Mapping) else {}
        self.mode = MODE
        self.real_orders = REAL_ORDERS
        self.ftmo_real = FTMO_REAL

    def safety_check(self) -> bool:
        return (
            self.mode == MODE
            and self.real_orders == REAL_ORDERS
            and self.ftmo_real == FTMO_REAL
        )

    def _decision(self, allowed: bool, route: str, reason: str,
                  edge_status: str, score: float = 0.0) -> ContextRouteDecision:
        return ContextRouteDecision(
            allowed=allowed,
            route=route,
            reason=reason,
            edge_status=edge_status,
            decision="PAPER_ELIGIBLE" if allowed else "OBSERVE_ONLY",
            real_execution_allowed=False,
            source_cluster=str(self.scored_edge.get("cluster_id", "")),
            source_edge=str(self.scored_edge.get("source_candidate_id", "")),
            edge_score=score,
            edge_score_decision=edge_status,
        )

    def route(self, context: Mapping[str, Any]) -> ContextRouteDecision:
        if not self.safety_check():
            return self._decision(False, "BLOCK", "SAFETY_LOCK_FAILED", "BLOCKED")
        if not isinstance(context, Mapping):
            return self._decision(False, "OBSERVE_ONLY", "INVALID_CONTEXT", "CONTEXT_INVALID")

        decision = self.scored_edge.get("decision", "UNKNOWN")
        try:
            score = float(self.scored_edge.get("final_score"))
        except (TypeError, ValueError):
            return self._decision(False, "OBSERVE_ONLY", "INVALID_EDGE_SCORE", str(decision))
        if not isfinite(score):
            return self._decision(False, "OBSERVE_ONLY", "INVALID_EDGE_SCORE", str(decision))

        if decision != "PROMOTE_SCORE":
            return self._decision(
                False, "OBSERVE_ONLY", f"EDGE_NOT_PROMOTED_SCORE_{score}", str(decision), score
            )

        expected_key = self.scored_edge.get("key")
        expected_direction = self.scored_edge.get("direction")
        actual_key = context.get("key")
        actual_direction = context.get("direction")

        if not isinstance(expected_key, str) or not expected_key.strip():
            return self._decision(False, "OBSERVE_ONLY", "MISSING_EDGE_KEY", str(decision), score)
        if not isinstance(expected_direction, str) or not expected_direction.strip():
            return self._decision(False, "OBSERVE_ONLY", "MISSING_EDGE_DIRECTION", str(decision), score)
        if actual_key != expected_key:
            return self._decision(False, "OBSERVE_ONLY", "CONTEXT_KEY_MISMATCH", str(decision), score)
        if actual_direction != expected_direction:
            return self._decision(False, "OBSERVE_ONLY", "CONTEXT_DIRECTION_MISMATCH", str(decision), score)

        if not str(self.scored_edge.get("cluster_id", "")).strip():
            return self._decision(False, "OBSERVE_ONLY", "MISSING_SOURCE_CLUSTER", str(decision), score)
        if not str(self.scored_edge.get("source_candidate_id", "")).strip():
            return self._decision(False, "OBSERVE_ONLY", "MISSING_SOURCE_EDGE", str(decision), score)

        return self._decision(
            True, "PAPER_SIGNAL_CANDIDATE", "PROMOTED_SCORE_CONTEXT_MATCH", str(decision), score
        )


def build_router(scored_edge: Mapping[str, Any]) -> P2395ContextRouterV2:
    return P2395ContextRouterV2(scored_edge)
