
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

class P2408PaperRuntimeIntegrationGated:
    def __init__(self, ensemble_members, router_policy):
        self.ensemble_members=list(ensemble_members or [])
        self.router_policy=dict(router_policy or {})

    def safety_check(self):
        return MODE=="PAPER_ONLY" and REAL_ORDERS=="FORBIDDEN" and FTMO_REAL=="FORBIDDEN"

    def dispatch(self, context):
        if not self.safety_check():
            return {"allowed":False,"route":"BLOCK","reason":"SAFETY_LOCK_FAILED","real_execution_allowed":False}

        if context.get("symbol") != self.router_policy.get("allowed_symbol","GER40"):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"SYMBOL_NOT_ALLOWED","real_execution_allowed":False}

        if context.get("timeframe") not in self.router_policy.get("allowed_timeframes",[]):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"TIMEFRAME_NOT_ALLOWED","real_execution_allowed":False}

        matched=[]
        for m in self.ensemble_members:
            score=0
            if m.get("session")==context.get("session"): score+=1
            if m.get("regime")==context.get("regime"): score+=1
            if m.get("timeframe")==context.get("timeframe"): score+=1
            if m.get("direction")==context.get("direction"): score+=1
            if score>=2: matched.append(m)

        weight_sum=sum(float(m.get("ensemble_weight",0)) for m in matched)
        quorum=int(self.router_policy.get("min_context_matches",3))
        confidence=min(1.0,weight_sum)

        if len(matched)<quorum:
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"QUORUM_NOT_REACHED","matches":len(matched),"real_execution_allowed":False}

        if confidence<float(self.router_policy.get("min_confidence",0.62)):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"CONFIDENCE_BELOW_GATE","confidence":confidence,"real_execution_allowed":False}

        return {
            "allowed":True,
            "route":"PAPER_SIGNAL_CANDIDATE",
            "reason":"PAPER_RUNTIME_GATE_APPROVED",
            "confidence":round(confidence,6),
            "matches":len(matched),
            "mode":MODE,
            "real_orders":REAL_ORDERS,
            "ftmo_real":FTMO_REAL,
            "real_execution_allowed":False
        }

def build_runtime(ensemble_members, router_policy):
    return P2408PaperRuntimeIntegrationGated(ensemble_members, router_policy)

def runtime_allowed():
    return False
