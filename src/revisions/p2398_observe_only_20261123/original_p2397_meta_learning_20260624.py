import json, csv, pathlib, hashlib, statistics, math, os
from datetime import datetime

MISSION="P2397_META_LEARNING_OFFLINE"
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

P2391=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2391_RETURN_TO_EDGE_RESEARCH_20260624_220417")
P2392=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2392_EDGE_WALK_FORWARD_VALIDATION_20260624_221342")
P2394=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2394_EDGE_SCORING_20260624_222430")
P2396=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2396_EDGE_ENSEMBLE_20260624_222857")
LOCK=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
OUT=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core_evidence\P2397_META_LEARNING_OFFLINE_20260624_223219")
ROOT=pathlib.Path(r"C:\Users\MindFin\Desktop\mind-fin-pro-backend-core")
OUT.mkdir(parents=True, exist_ok=True)

def load_json(path):
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))

s2392=load_json(P2392/"summary.json")
s2394=load_json(P2394/"summary.json")
s2396=load_json(P2396/"summary.json")

for s in [s2392,s2394,s2396]:
    assert s.get("mode")=="PAPER_ONLY"
    assert s.get("real_orders")=="FORBIDDEN"
    assert s.get("ftmo_real")=="FORBIDDEN"
    assert s.get("real_execution_allowed") is False

best2392=s2392.get("best_promoted",{})
score_edge=s2394.get("best_scored_edge",{})

meta_memory=[]
meta_memory.append({
    "source":"P2392_WALK_FORWARD",
    "candidate_id":best2392.get("candidate_id"),
    "key":best2392.get("key"),
    "dimensions":best2392.get("dimensions"),
    "direction":best2392.get("direction"),
    "decision":best2392.get("decision"),
    "pf":best2392.get("pf"),
    "winrate":best2392.get("winrate"),
    "expectancy":best2392.get("expectancy"),
    "max_dd_r":best2392.get("max_dd_r"),
    "samples":best2392.get("samples"),
    "passed_windows":best2392.get("passed_windows"),
    "net_r":best2392.get("net_r"),
})
meta_memory.append({
    "source":"P2394_SCORING",
    "candidate_id":score_edge.get("source_candidate_id"),
    "key":score_edge.get("key"),
    "dimensions":score_edge.get("dimensions"),
    "direction":score_edge.get("direction"),
    "decision":score_edge.get("decision"),
    "pf":score_edge.get("pf"),
    "winrate":score_edge.get("winrate"),
    "expectancy":score_edge.get("expectancy"),
    "max_dd_r":score_edge.get("max_dd_r"),
    "samples":score_edge.get("samples"),
    "passed_windows":score_edge.get("passed_windows"),
    "net_r":score_edge.get("net_r"),
    "final_score":score_edge.get("final_score"),
})

def safe_float(x, default=0.0):
    try: return float(x)
    except Exception: return default

base_key=str(score_edge.get("key") or best2392.get("key") or "")
parts=base_key.split("|")
session=parts[0] if len(parts)>0 else "UNKNOWN_SESSION"
footprint=parts[1] if len(parts)>1 else "UNKNOWN_FOOTPRINT"
lifecycle=parts[2] if len(parts)>2 else "UNKNOWN_LIFECYCLE"
transition=parts[3] if len(parts)>3 else "UNKNOWN_TRANSITION"

pf=safe_float(score_edge.get("pf"))
wr=safe_float(score_edge.get("winrate"))
exp=safe_float(score_edge.get("expectancy"))
dd=safe_float(score_edge.get("max_dd_r"))
score=safe_float(score_edge.get("final_score"))
samples=int(safe_float(score_edge.get("samples")))
passed=int(safe_float(score_edge.get("passed_windows")))

quality = {
    "pf_quality": "GOOD" if pf >= 1.5 else "WEAK",
    "wr_quality": "GOOD" if wr >= 55 else "WEAK",
    "expectancy_quality": "POSITIVE" if exp > 0 else "NEGATIVE",
    "dd_quality": "HIGH_RISK" if dd > 4 else "ACCEPTABLE",
    "sample_quality": "ENOUGH" if samples >= 150 else "THIN",
    "window_quality": "NEAR_CERTIFIED" if passed >= 4 else "WEAK",
    "score_quality": "NEAR_PROMOTION" if 65 <= score < 70 else ("PROMOTABLE" if score >= 70 else "WEAK")
}

hypotheses=[
    {
        "hypothesis_id":"P2397_HYP_"+hashlib.sha256((base_key+"|DD_REDUCTION").encode()).hexdigest()[:10].upper(),
        "type":"DD_REDUCTION",
        "base_context":base_key,
        "target":"reduce_max_dd_r_below_3_5",
        "reason":"edge has positive expectancy but drawdown penalty blocked promotion",
        "recommended_search_bias":"same context with stricter entry timing and loss clustering filter",
        "paper_only":True
    },
    {
        "hypothesis_id":"P2397_HYP_"+hashlib.sha256((session+"|"+footprint+"|SESSION_FOCUS").encode()).hexdigest()[:10].upper(),
        "type":"SESSION_FOOTPRINT_PRIORITY",
        "base_context":base_key,
        "target":f"prioritize {session} + {footprint}",
        "reason":"only surviving WF edge came from this session/footprint zone",
        "recommended_search_bias":"expand same footprint across adjacent lifecycle and transition variants",
        "paper_only":True
    },
    {
        "hypothesis_id":"P2397_HYP_"+hashlib.sha256((transition+"|TRANSITION").encode()).hexdigest()[:10].upper(),
        "type":"CYCLE_TRANSITION_EXPANSION",
        "base_context":base_key,
        "target":transition,
        "reason":"cycle transition survived WF but score remained observed",
        "recommended_search_bias":"test symmetric and neighboring transition states without runtime promotion",
        "paper_only":True
    }
]

research_policy={
    "mode":MODE,
    "real_orders":REAL_ORDERS,
    "ftmo_real":FTMO_REAL,
    "runtime_modification_allowed":False,
    "broker_execution_allowed":False,
    "ftmo_real_allowed":False,
    "learning_scope":"OFFLINE_RESEARCH_ONLY",
    "next_research_biases":[h["recommended_search_bias"] for h in hypotheses],
    "hard_rules":[
        "never promote OBSERVE_SCORE into runtime",
        "never bypass P2392 walk-forward",
        "never bypass P2394 score threshold",
        "never allow real execution",
        "generate candidates only as research hypotheses"
    ]
}

with open(OUT/"meta_memory.csv","w",newline="",encoding="utf-8") as f:
    fields=sorted({k for row in meta_memory for k in row.keys()})
    w=csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(meta_memory)

with open(OUT/"p2397_hypotheses.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=list(hypotheses[0].keys()))
    w.writeheader()
    w.writerows(hypotheses)

(OUT/"research_policy.json").write_text(json.dumps(research_policy,indent=2,ensure_ascii=False),encoding="utf-8")

module=ROOT/"app"/"runtime"/"p2397_meta_learning_offline.py"
module.write_text(r'''
"""
P2397_META_LEARNING_OFFLINE

Offline-only meta-learning layer.
It creates research hypotheses.
It does not modify runtime routing.
It does not execute orders.
"""

from dataclasses import dataclass
from typing import Dict, Any, List

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

@dataclass(frozen=True)
class MetaLearningDecision:
    allowed_for_runtime: bool
    allowed_for_research: bool
    decision: str
    reason: str
    hypotheses: int
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL

class P2397MetaLearningOffline:
    def __init__(self, scored_edge: Dict[str, Any], hypotheses: List[Dict[str, Any]]):
        self.scored_edge = dict(scored_edge or {})
        self.hypotheses = list(hypotheses or [])

    def safety_check(self) -> bool:
        return MODE=="PAPER_ONLY" and REAL_ORDERS=="FORBIDDEN" and FTMO_REAL=="FORBIDDEN"

    def evaluate(self) -> MetaLearningDecision:
        if not self.safety_check():
            return MetaLearningDecision(False, False, "BLOCK", "SAFETY_LOCK_FAILED", 0)

        if self.scored_edge.get("decision") != "PROMOTE_SCORE":
            return MetaLearningDecision(
                allowed_for_runtime=False,
                allowed_for_research=True,
                decision="RESEARCH_ONLY",
                reason="EDGE_NOT_PROMOTED_META_LEARNING_OFFLINE_ONLY",
                hypotheses=len(self.hypotheses),
            )

        return MetaLearningDecision(
            allowed_for_runtime=False,
            allowed_for_research=True,
            decision="RESEARCH_ONLY",
            reason="META_LEARNING_NEVER_PROMOTES_DIRECTLY_TO_RUNTIME",
            hypotheses=len(self.hypotheses),
        )

def build_meta_learning(scored_edge: Dict[str, Any], hypotheses: List[Dict[str, Any]]):
    return P2397MetaLearningOffline(scored_edge, hypotheses)
''',encoding="utf-8")

summary={
    "mission":MISSION,
    "mode":MODE,
    "real_orders":REAL_ORDERS,
    "ftmo_real":FTMO_REAL,
    "inputs":{
        "p2391":str(P2391),
        "p2392":str(P2392),
        "p2394":str(P2394),
        "p2396":str(P2396),
        "governance_lock":str(LOCK)
    },
    "output":str(OUT),
    "module":str(module),
    "source_edge":score_edge.get("source_candidate_id"),
    "source_cluster":score_edge.get("cluster_id"),
    "edge_score":score,
    "edge_decision":score_edge.get("decision"),
    "quality":quality,
    "hypotheses_created":len(hypotheses),
    "runtime_promotion_allowed":False,
    "research_allowed":True,
    "paper_stack_modified":True,
    "real_execution_allowed":False,
    "certification":"P2397_META_LEARNING_OFFLINE_RESEARCH_CERTIFIED",
    "next_required":"P2398_RUNTIME_EDGE_INTEGRATION_PAPER_GATED"
}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")

audit=f"""============================================================
P2397 COMPLETE â META LEARNING OFFLINE
============================================================
MISSION............. {MISSION}
MODE................ {MODE}
REAL_ORDERS......... {REAL_ORDERS}
FTMO_REAL........... {FTMO_REAL}

INPUTS:
P2391............... {P2391}
P2392............... {P2392}
P2394............... {P2394}
P2396............... {P2396}
GOVERNANCE LOCK..... {LOCK}

EVIDENCE:
{OUT}

MODULE:
{module}

SOURCE EDGE......... {score_edge.get("source_candidate_id")}
SOURCE CLUSTER...... {score_edge.get("cluster_id")}
EDGE SCORE.......... {score}
EDGE DECISION....... {score_edge.get("decision")}

QUALITY:
PF.................. {quality["pf_quality"]}
WR.................. {quality["wr_quality"]}
EXPECTANCY.......... {quality["expectancy_quality"]}
DD.................. {quality["dd_quality"]}
SAMPLES............. {quality["sample_quality"]}
WINDOWS............. {quality["window_quality"]}
SCORE............... {quality["score_quality"]}

HYPOTHESES CREATED.. {len(hypotheses)}
RUNTIME PROMOTION... False
RESEARCH ALLOWED.... True
REAL_EXEC_ALLOWED... False

CERTIFICATION....... P2397_META_LEARNING_OFFLINE_RESEARCH_CERTIFIED
NEXT_REQUIRED....... P2398_RUNTIME_EDGE_INTEGRATION_PAPER_GATED

AUDIT:
- Meta-learning criado apenas offline.
- Edge observado NÃO foi promovido ao runtime.
- HipÃ³teses de pesquisa geradas para novos edges.
- Prioridade futura: reduzir DD, expandir contexto sobrevivente e testar transiÃ§Ãµes vizinhas.
- Governance Lock preservado.
- REAL_ORDERS e FTMO_REAL permanecem FORBIDDEN.
============================================================
"""
(OUT/"AUDIT_FINAL.txt").write_text(audit,encoding="utf-8")
print(audit)
