
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

class GlobalSwitchboard:
    def __init__(self, registry):
        self.registry=list(registry or [])
        self.by_domain={}
        for r in self.registry:
            self.by_domain.setdefault(r.get("domain","UNKNOWN"),[]).append(r)

    def safety_contract(self):
        return {
            "mode":MODE,
            "real_orders":REAL_ORDERS,
            "ftmo_real":FTMO_REAL,
            "real_execution_allowed":False,
            "paper_only":True,
            "domains":sorted(self.by_domain.keys()),
            "capabilities":len(self.registry)
        }

    def route(self, domain, payload=None):
        caps=self.by_domain.get(domain,[])
        if not caps:
            return {"ok":False,"route":"OBSERVE_ONLY","reason":"DOMAIN_NOT_FOUND","real_execution_allowed":False}
        return {
            "ok":True,
            "route":"PAPER_OBSERVE_CAPABILITY_GROUP",
            "domain":domain,
            "capabilities":len(caps),
            "real_execution_allowed":False
        }

def runtime_allowed():
    return False

def build_switchboard(registry):
    return GlobalSwitchboard(registry)
