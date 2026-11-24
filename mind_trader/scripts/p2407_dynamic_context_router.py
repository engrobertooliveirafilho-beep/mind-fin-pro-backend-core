class P2407DynamicContextRouter:
    def __init__(self, members, policy):
        self.members = tuple(members or ())
        self.policy = dict(policy or {})

    def safety_check(self):
        return (self.policy.get("mode") == "PAPER_ONLY"
                and self.policy.get("real_orders") == "FORBIDDEN"
                and self.policy.get("ftmo_real") == "FORBIDDEN"
                and self.policy.get("real_execution_allowed") is False)

    def route(self, context):
        return {"allowed": False, "route": "BLOCK",
                "reason": "P2406_PROVENANCE_UNCERTIFIED" if self.safety_check() else "SAFETY_LOCK_FAILED",
                "matches": 0, "confidence": 0.0, "mode": "PAPER_ONLY",
                "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
                "real_execution_allowed": False}

def build_router(members, policy):
    return P2407DynamicContextRouter(members, policy)

def runtime_allowed():
    return False
