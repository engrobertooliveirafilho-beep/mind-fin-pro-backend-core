"""P2406: contextual quorum, directional support and family concentration."""
from dataclasses import dataclass
from math import isfinite

MODE="PAPER_ONLY"; REAL_ORDERS="FORBIDDEN"; FTMO_REAL="FORBIDDEN"
REQUIRED_CONTEXT={"session","regime","timeframe","direction"}

@dataclass(frozen=True)
class EnsembleDecision:
    allowed: bool
    route: str
    confidence: float
    quorum: int
    votes: int
    reason: str
    family_concentration: float
    mode: str=MODE
    real_orders: str=REAL_ORDERS
    ftmo_real: str=FTMO_REAL

class P2406EdgeEnsembleOptimizer:
    def __init__(self,members,min_quorum=3,min_confidence=.62,max_family_concentration=.40):
        self.members=list(members or []); self.min_quorum=int(min_quorum)
        self.min_confidence=float(min_confidence); self.max_family_concentration=float(max_family_concentration)
        if self.min_quorum<1 or not 0<self.min_confidence<=1 or not 0<self.max_family_concentration<=1:
            raise ValueError("Invalid ensemble policy")
    def vote(self,context):
        def block(reason,votes=0,confidence=0.0,concentration=0.0):
            return EnsembleDecision(False,"OBSERVE_ONLY",confidence,self.min_quorum,votes,reason,concentration)
        if MODE!="PAPER_ONLY" or REAL_ORDERS!="FORBIDDEN" or FTMO_REAL!="FORBIDDEN":
            return EnsembleDecision(False,"BLOCK",0.0,self.min_quorum,0,"SAFETY_LOCK_FAILED",0.0)
        if not isinstance(context,dict) or not REQUIRED_CONTEXT<=set(context): return block("CONTEXT_INCOMPLETE")
        active=[]; seen=set()
        for m in self.members:
            if m.get("status")!="ENSEMBLE_MEMBER": continue
            eid=str(m.get("edge_id",""))
            if not eid or eid in seen: return block("DUPLICATE_OR_MISSING_EDGE_ID")
            seen.add(eid)
            if any(m.get(k)!=context.get(k) for k in ("session","regime","timeframe")): continue
            w=float(m.get("ensemble_weight",0.0))
            if not isfinite(w) or w<0: return block("INVALID_WEIGHT")
            if w>0: active.append(m)
        votes=len(active)
        if votes<self.min_quorum: return block("QUORUM_NOT_REACHED",votes)
        total=sum(float(m["ensemble_weight"]) for m in active)
        if total<=0: return block("ZERO_WEIGHT",votes)
        families={}
        for m in active:
            fam=str(m.get("family","")).strip()
            if not fam: return block("FAMILY_MISSING",votes)
            families[fam]=families.get(fam,0.0)+float(m["ensemble_weight"])
        concentration=max(families.values())/total
        if concentration>self.max_family_concentration+1e-12:
            return block("FAMILY_CONCENTRATION_EXCEEDED",votes,0.0,concentration)
        target=str(context["direction"]).upper()
        if target not in {"BUY","SELL","BUY_PAPER","SELL_PAPER"}: return block("INVALID_DIRECTION",votes,0.0,concentration)
        target="BUY" if target.startswith("BUY") else "SELL"
        support=sum(float(m["ensemble_weight"]) for m in active if str(m.get("direction","")).upper().startswith(target))
        confidence=support/total
        if confidence<self.min_confidence: return block("CONFIDENCE_BELOW_GATE",votes,confidence,concentration)
        return EnsembleDecision(True,"PAPER_SIGNAL_CANDIDATE",confidence,self.min_quorum,votes,
            "CONTEXTUAL_QUORUM_APPROVED",concentration)

def build_ensemble(members,min_quorum=3,min_confidence=.62,max_family_concentration=.40):
    return P2406EdgeEnsembleOptimizer(members,min_quorum,min_confidence,max_family_concentration)
def runtime_allowed(): return False
