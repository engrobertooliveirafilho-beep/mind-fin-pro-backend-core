from dataclasses import dataclass
from collections import defaultdict
MODE="PAPER_ONLY"; REAL_ORDERS="FORBIDDEN"; FTMO_REAL="FORBIDDEN"
@dataclass(frozen=True)
class Decision:
    allowed: bool; route: str; confidence: float; votes: int; quorum: int; reason: str

def contextual_vote(members,context,min_quorum=3,min_confidence=.62,max_family_concentration=.40):
    if MODE!="PAPER_ONLY" or REAL_ORDERS!="FORBIDDEN" or FTMO_REAL!="FORBIDDEN":
        return Decision(False,"BLOCK",0.0,0,min_quorum,"SAFETY_LOCK_FAILED")
    required={"session","regime","timeframe","direction"}
    if not context or not required.issubset(context):
        return Decision(False,"OBSERVE_ONLY",0.0,0,min_quorum,"CONTEXT_INCOMPLETE")
    active=[]
    for m in members:
        if m.get("status")!="ENSEMBLE_MEMBER": continue
        if any(m.get(k)!=context[k] for k in required): continue
        w=float(m.get("ensemble_weight",0))
        if w>0: active.append((m,w))
    votes=len(active)
    if votes<min_quorum: return Decision(False,"OBSERVE_ONLY",0.0,votes,min_quorum,"QUORUM_NOT_REACHED")
    total=sum(w for _,w in active)
    if total<=0: return Decision(False,"OBSERVE_ONLY",0.0,votes,min_quorum,"ZERO_WEIGHT")
    families=defaultdict(float)
    for m,w in active: families[m.get("family","UNKNOWN")]+=w
    concentration=max(families.values())/total
    if concentration>max_family_concentration:
        return Decision(False,"OBSERVE_ONLY",concentration,votes,min_quorum,"FAMILY_CONCENTRATION_EXCEEDED")
    confidence=min(1.0,total)
    if confidence<min_confidence: return Decision(False,"OBSERVE_ONLY",confidence,votes,min_quorum,"CONFIDENCE_BELOW_GATE")
    return Decision(True,"PAPER_SIGNAL_CANDIDATE",confidence,votes,min_quorum,"CONTEXTUAL_QUORUM_APPROVED")

def runtime_allowed(): return False
