import math
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

def _deny(reason="SAFETY_VALIDATION_FAILED"):
    return {"allowed":False,"route":"BLOCK","reason":reason,"real_execution_allowed":False}

def _number(value,low,high):
    if isinstance(value,bool): raise ValueError("boolean")
    n=float(value)
    if not math.isfinite(n) or not low<=n<=high: raise ValueError("invalid")
    return n

class P2408PaperRuntimeIntegrationGated:
    def __init__(self,ensemble_members,router_policy):
        self.ensemble_members=ensemble_members
        self.router_policy=router_policy

    def safety_check(self):
        p=self.router_policy
        return (isinstance(p,dict) and MODE=="PAPER_ONLY" and REAL_ORDERS=="FORBIDDEN"
                and FTMO_REAL=="FORBIDDEN" and p.get("mode")==MODE
                and p.get("real_orders")==REAL_ORDERS and p.get("ftmo_real")==FTMO_REAL
                and p.get("real_execution_allowed") is False)

    def dispatch(self,context):
        if not self.safety_check(): return _deny("SAFETY_LOCK_FAILED")
        p=self.router_policy
        if not isinstance(context,dict) or not isinstance(self.ensemble_members,list): return _deny()
        if (context.get("mode",MODE)!=MODE or context.get("real_orders",REAL_ORDERS)!=REAL_ORDERS
            or context.get("ftmo_real",FTMO_REAL)!=FTMO_REAL
            or context.get("real_execution_allowed",False) is not False): return _deny()
        if context.get("direction") not in ("BUY_PAPER","SELL_PAPER"): return _deny("DIRECTION_NOT_ALLOWED")
        for field,key in (("allowed_sessions","session"),("allowed_regimes","regime"),("allowed_timeframes","timeframe")):
            values=p.get(field)
            if not isinstance(values,(list,tuple)) or not values or context.get(key) not in values:
                return _deny(key.upper()+"_NOT_ALLOWED")
        if not isinstance(p.get("allowed_symbol"),str) or context.get("symbol")!=p["allowed_symbol"]:
            return _deny("SYMBOL_NOT_ALLOWED")
        if not self.ensemble_members: return _deny("EMPTY_ENSEMBLE")
        try:
            quorum=_number(p.get("min_context_matches"),1,100000)
            if not quorum.is_integer(): return _deny()
            threshold=_number(p.get("min_confidence"),0,1)
            min_weight=_number(p.get("min_weight_sum",0),0,1)
            matched=[]
            for m in self.ensemble_members:
                if not isinstance(m,dict): return _deny()
                weight=_number(m.get("ensemble_weight"),0,1)
                score=sum(m.get(k)==context.get(k) for k in ("session","regime","timeframe","direction"))
                if score>=2: matched.append(weight)
            total=sum(matched)
            if not math.isfinite(total): return _deny()
        except (TypeError,ValueError,OverflowError): return _deny()
        if len(matched)<int(quorum):
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"QUORUM_NOT_REACHED",
                    "matches":len(matched),"real_execution_allowed":False}
        if total<min_weight or min(1.,total)<threshold:
            return {"allowed":False,"route":"OBSERVE_ONLY","reason":"CONFIDENCE_BELOW_GATE",
                    "real_execution_allowed":False}
        return {"allowed":True,"route":"PAPER_SIGNAL_CANDIDATE",
                "reason":"PAPER_RUNTIME_GATE_APPROVED","confidence":round(min(1.,total),6),
                "matches":len(matched),"mode":MODE,"real_orders":REAL_ORDERS,
                "ftmo_real":FTMO_REAL,"real_execution_allowed":False}

def build_runtime(ensemble_members,router_policy):
    return P2408PaperRuntimeIntegrationGated(ensemble_members,router_policy)

def runtime_allowed():
    return False
