from .p2406_edge_ensemble_optimizer import build_ensemble
from .p2407_dynamic_context_router import build_router

class P2408PaperRuntimeIntegrationGated:
    def __init__(self, ensemble_members, router_policy):
        self.ensemble = build_ensemble(ensemble_members)
        self.router = build_router(ensemble_members, router_policy)

    def dispatch(self, context):
        reason = "P2408_CERTIFICATION_PENDING"
        try:
            vote = self.ensemble.vote(context)
            route = self.router.route(context)
            if not vote.allowed:
                reason = vote.reason
            elif route.get("allowed") is not True:
                reason = route.get("reason", "ROUTER_BLOCKED")
        except Exception:
            reason = "DEPENDENCY_FAILURE"
        return dict(allowed=False, route="BLOCK", reason=reason,
                    mode="PAPER_ONLY", real_orders="FORBIDDEN",
                    ftmo_real="FORBIDDEN", real_execution_allowed=False)

def build_runtime(ensemble_members, router_policy):
    return P2408PaperRuntimeIntegrationGated(ensemble_members, router_policy)

def runtime_allowed():
    return False
