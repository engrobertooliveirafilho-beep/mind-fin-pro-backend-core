
from typing import List, Dict, Any

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

class P2407DynamicContextRouter:
    def __init__(self, members: List[Dict[str, Any]], policy: Dict[str, Any]):
        self.members=list(members or [])
        self.policy=dict(policy or {})

    def safety_check(self):
        return MODE=="PAPER_ONLY" and REAL_ORDERS=="FORBIDDEN" and FTMO_REAL=="FORBIDDEN"

    def route(self, context: Dict[str, Any]):
        if not self.safety_check():
            return {"allowed":False,"route":"BLOCK","reason":"SAFETY_LOCK_FAILED"}

        if context.get("symbol") != self.policy.get("allowed_symbol","GER40"):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"SYMBOL_NOT_ALLOWED"}

        if context.get("timeframe") not in self.policy.get("allowed_timeframes",[]):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"TIMEFRAME_NOT_ALLOWED"}

        matched=[]
        for m in self.members:
            score=0
            if m.get("session")==context.get("session"): score+=1
            if m.get("regime")==context.get("regime"): score+=1
            if m.get("timeframe")==context.get("timeframe"): score+=1
            if m.get("direction")==context.get("direction"): score+=1
            if score>=2:
                matched.append(m)

        weight_sum=sum(float(m.get("ensemble_weight",0)) for m in matched)
        confidence=min(1.0, weight_sum)

        if len(matched) < int(self.policy.get("min_context_matches",3)):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"INSUFFICIENT_CONTEXT_MATCHES","matches":len(matched)}

        if weight_sum < float(self.policy.get("min_weight_sum",0.40)):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"INSUFFICIENT_WEIGHT_SUM","matches":len(matched)}

        if confidence < float(self.policy.get("min_confidence",0.62)):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"CONFIDENCE_BELOW_GATE","matches":len(matched)}

        return {
            "allowed":True,
            "route":"PAPER_SIGNAL_CANDIDATE",
            "reason":"CONTEXT_ROUTER_APPROVED",
            "matches":len(matched),
            "confidence":round(confidence,6),
            "mode":MODE,
            "real_orders":REAL_ORDERS,
            "ftmo_real":FTMO_REAL
        }

def runtime_allowed():
    return False

def build_router(members, policy):
    return P2407DynamicContextRouter(members, policy)
