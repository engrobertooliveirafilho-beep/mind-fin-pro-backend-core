
"""
P2395_CONTEXT_ROUTER_V2
PAPER_ONLY context router.

Safety:
- REAL_ORDERS forbidden.
- FTMO_REAL forbidden.
- No broker execution.
- No order placement.
"""

from dataclasses import dataclass
from typing import Dict, Any


MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


@dataclass(frozen=True)
class ContextRouteDecision:
    allowed: bool
    route: str
    reason: str
    edge_status: str
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL


class P2395ContextRouterV2:
    def __init__(self, scored_edge: Dict[str, Any]):
        self.scored_edge = dict(scored_edge or {})
        self.mode = MODE
        self.real_orders = REAL_ORDERS
        self.ftmo_real = FTMO_REAL

    def safety_check(self) -> bool:
        return (
            self.mode == "PAPER_ONLY"
            and self.real_orders == "FORBIDDEN"
            and self.ftmo_real == "FORBIDDEN"
        )

    def route(self, context: Dict[str, Any]) -> ContextRouteDecision:
        if not self.safety_check():
            return ContextRouteDecision(False, "BLOCK", "SAFETY_LOCK_FAILED", "BLOCKED")

        decision = self.scored_edge.get("decision", "UNKNOWN")
        score = float(self.scored_edge.get("final_score", 0) or 0)

        if decision != "PROMOTE_SCORE":
            return ContextRouteDecision(
                allowed=False,
                route="OBSERVE_ONLY",
                reason=f"EDGE_NOT_PROMOTED_SCORE_{score}",
                edge_status=decision,
            )

        key = str(self.scored_edge.get("key", ""))
        direction = str(self.scored_edge.get("direction", ""))

        if not key or not direction:
            return ContextRouteDecision(False, "BLOCK", "MISSING_CONTEXT_KEY_OR_DIRECTION", decision)

        return ContextRouteDecision(
            allowed=True,
            route="PAPER_SIGNAL_CANDIDATE",
            reason="PROMOTED_SCORE_CONTEXT_MATCH",
            edge_status=decision,
        )


def build_router(scored_edge: Dict[str, Any]) -> P2395ContextRouterV2:
    return P2395ContextRouterV2(scored_edge)
