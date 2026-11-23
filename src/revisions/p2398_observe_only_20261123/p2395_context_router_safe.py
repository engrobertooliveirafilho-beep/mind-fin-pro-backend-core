"""Isolated P2395 read-only router; never grants runtime execution."""
from collections.abc import Mapping
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class ContextRouteDecision:
    allowed: bool
    route: str
    reason: str
    edge_status: str
    mode: str = 'PAPER_ONLY'
    real_orders: str = 'FORBIDDEN'
    ftmo_real: str = 'FORBIDDEN'

class P2395ContextRouterV2:
    def __init__(self, scored_edge):
        self.scored_edge = dict(scored_edge) if isinstance(scored_edge, Mapping) else {}

    def route(self, context):
        edge = self.scored_edge
        decision = edge.get('decision')
        if decision != 'OBSERVE_SCORE':
            return ContextRouteDecision(False, 'BLOCK', 'UNAUTHORIZED_EDGE_DECISION', str(decision))
        score = edge.get('final_score')
        if type(score) not in (int, float) or not math.isfinite(score) or score != 68.391266:
            return ContextRouteDecision(False, 'BLOCK', 'INVALID_HISTORICAL_SCORE', decision)
        if not isinstance(context, Mapping):
            return ContextRouteDecision(False, 'BLOCK', 'INVALID_CONTEXT', decision)
        if set(context) != {'key', 'direction', 'mode', 'real_orders', 'ftmo_real'}:
            return ContextRouteDecision(False, 'BLOCK', 'INVALID_CONTEXT_SCHEMA', decision)
        if (context['mode'], context['real_orders'], context['ftmo_real']) != ('PAPER_ONLY', 'FORBIDDEN', 'FORBIDDEN'):
            return ContextRouteDecision(False, 'BLOCK', 'UNSAFE_CONTEXT', decision)
        for field in ('key', 'direction'):
            value = edge.get(field)
            if not isinstance(value, str) or not value.strip() or context[field] != value:
                return ContextRouteDecision(False, 'BLOCK', 'CONTEXT_MISMATCH', decision)
        return ContextRouteDecision(False, 'OBSERVE_ONLY', 'P2394_NOT_PROMOTED', decision)

def build_router(scored_edge):
    return P2395ContextRouterV2(scored_edge)
