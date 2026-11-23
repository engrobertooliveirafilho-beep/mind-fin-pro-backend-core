"""Isolated P2396 PAPER-only ensemble: observations cannot authorize orders."""
from collections.abc import Mapping
from dataclasses import dataclass

@dataclass(frozen=True)
class EnsembleVote:
    allowed: bool
    vote: str
    reason: str
    members: int
    operational_members: int
    mode: str = 'PAPER_ONLY'
    real_orders: str = 'FORBIDDEN'
    ftmo_real: str = 'FORBIDDEN'

class P2396EdgeEnsemble:
    def __init__(self, router_decisions, quorum=2):
        self.decisions = router_decisions
        self.quorum = quorum

    def vote(self):
        rows = self.decisions
        if not isinstance(rows, (tuple, list)) or type(self.quorum) is not int or self.quorum < 2:
            return EnsembleVote(False, 'BLOCK', 'INVALID_ENSEMBLE_INPUT', 0, 0)
        if any(not isinstance(row, Mapping) for row in rows):
            return EnsembleVote(False, 'BLOCK', 'INVALID_MEMBER', len(rows), 0)
        seen = set()
        for row in rows:
            if row.get('allowed') is not False or row.get('route') != 'OBSERVE_ONLY':
                return EnsembleVote(False, 'BLOCK', 'UNAUTHORIZED_MEMBER', len(rows), 0)
            if (row.get('mode'), row.get('real_orders'), row.get('ftmo_real')) != ('PAPER_ONLY', 'FORBIDDEN', 'FORBIDDEN'):
                return EnsembleVote(False, 'BLOCK', 'UNSAFE_MEMBER', len(rows), 0)
            source = row.get('source_edge')
            if not isinstance(source, str) or not source.strip() or source in seen:
                return EnsembleVote(False, 'BLOCK', 'MISSING_OR_DUPLICATE_SOURCE', len(rows), 0)
            seen.add(source)
        return EnsembleVote(False, 'OBSERVE_ONLY', 'INSUFFICIENT_OPERATIONAL_QUORUM', len(rows), 0)

def build_ensemble(router_decisions, quorum=2):
    return P2396EdgeEnsemble(router_decisions, quorum)
