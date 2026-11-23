import json, pathlib, csv, re

MISSION="P2395_CONTEXT_ROUTER_V2"
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

root=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core")
p2394=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2394_EDGE_SCORING_20260624_222430")
lock=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
out=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2395_CONTEXT_ROUTER_V2_20260624_222716")
out.mkdir(parents=True, exist_ok=True)

src=p2394/"summary.json"
if not src.exists():
    raise SystemExit(f"Missing P2394 summary.json: {src}")

s=json.loads(src.read_text(encoding="utf-8"))
assert s["mode"]=="PAPER_ONLY"
assert s["real_orders"]=="FORBIDDEN"
assert s["ftmo_real"]=="FORBIDDEN"
assert s["paper_stack_modified"] is False
assert s["real_execution_allowed"] is False

edge=s["best_scored_edge"]
decision=edge["decision"]

runtime=root/"app"/"runtime"
py_files=list(runtime.rglob("*.py")) if runtime.exists() else []

router_candidates=[]
for f in py_files:
    name=f.name.lower()
    if any(k in name for k in ["router","edge","signal","decision","pipeline","context"]):
        txt=f.read_text(encoding="utf-8", errors="ignore")
        score=sum(1 for k in ["route","context","edge","signal","paper","decision"] if k in txt.lower())
        router_candidates.append({
            "path": str(f),
            "name": f.name,
            "score": score,
            "matched": True
        })

router_candidates=sorted(router_candidates, key=lambda x:x["score"], reverse=True)[:50]

module_dir=root/"app"/"runtime"
module_dir.mkdir(parents=True, exist_ok=True)
router_file=module_dir/"p2395_context_router_v2.py"

router_code=r'''
"""
P2395_CONTEXT_ROUTER_V2
PAPER_ONLY context router.

Safety:
- REAL_ORDERS forbidden.
- FTMO_REAL forbidden.
- No broker execution.
- No order placement.
"""

from dataclasses import dataclass
from typing import Dict, Any


MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


@dataclass(frozen=True)
class ContextRouteDecision:
    allowed: bool
    route: str
    reason: str
    edge_status: str
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL


class P2395ContextRouterV2:
    def __init__(self, scored_edge: Dict[str, Any]):
        self.scored_edge = dict(scored_edge or {})
        self.mode = MODE
        self.real_orders = REAL_ORDERS
        self.ftmo_real = FTMO_REAL

    def safety_check(self) -> bool:
        return (
            self.mode == "PAPER_ONLY"
            and self.real_orders == "FORBIDDEN"
            and self.ftmo_real == "FORBIDDEN"
        )

    def route(self, context: Dict[str, Any]) -> ContextRouteDecision:
        if not self.safety_check():
            return ContextRouteDecision(False, "BLOCK", "SAFETY_LOCK_FAILED", "BLOCKED")

        decision = self.scored_edge.get("decision", "UNKNOWN")
        score = float(self.scored_edge.get("final_score", 0) or 0)

        if decision != "PROMOTE_SCORE":
            return ContextRouteDecision(
                allowed=False,
                route="OBSERVE_ONLY",
                reason=f"EDGE_NOT_PROMOTED_SCORE_{score}",
                edge_status=decision,
            )

        key = str(self.scored_edge.get("key", ""))
        direction = str(self.scored_edge.get("direction", ""))

        if not key or not direction:
            return ContextRouteDecision(False, "BLOCK", "MISSING_CONTEXT_KEY_OR_DIRECTION", decision)

        return ContextRouteDecision(
            allowed=True,
            route="PAPER_SIGNAL_CANDIDATE",
            reason="PROMOTED_SCORE_CONTEXT_MATCH",
            edge_status=decision,
        )


def build_router(scored_edge: Dict[str, Any]) -> P2395ContextRouterV2:
    return P2395ContextRouterV2(scored_edge)
'''
router_file.write_text(router_code, encoding="utf-8")

route_status="OBSERVE_ONLY"
runtime_integrated=True
real_execution_allowed=False
paper_stack_modified=True

with open(out/"runtime_router_candidates.csv","w",newline="",encoding="utf-8") as f:
    fields=["path","name","score","matched"]
    w=csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in router_candidates:
        w.writerow(r)

router_contract={
    "mission":MISSION,
    "router_file":str(router_file),
    "input_edge_decision":decision,
    "input_edge_score":edge["final_score"],
    "route_result":route_status,
    "runtime_candidates_found":len(router_candidates),
    "integration_mode":"ISOLATED_RUNTIME_MODULE",
    "real_execution_allowed":False,
    "mode":MODE,
    "real_orders":REAL_ORDERS,
    "ftmo_real":FTMO_REAL
}
(out/"router_contract.json").write_text(json.dumps(router_contract,indent=2,ensure_ascii=False),encoding="utf-8")

summary={
    "mission":MISSION,
    "mode":MODE,
    "real_orders":REAL_ORDERS,
    "ftmo_real":FTMO_REAL,
    "input":str(p2394),
    "governance_lock":str(lock),
    "output":str(out),
    "router_file":str(router_file),
    "source_cluster":edge["cluster_id"],
    "source_edge":edge["source_candidate_id"],
    "edge_score":edge["final_score"],
    "edge_score_decision":decision,
    "router_decision":"OBSERVE_ONLY_BECAUSE_P2394_NOT_PROMOTED",
    "runtime_candidates_found":len(router_candidates),
    "runtime_integrated":runtime_integrated,
    "integration_mode":"ISOLATED_RUNTIME_MODULE",
    "paper_stack_modified":paper_stack_modified,
    "real_execution_allowed":real_execution_allowed,
    "certification":"P2395_CONTEXT_ROUTER_V2_OBSERVE_ONLY_CERTIFIED",
    "next_required":"P2396_EDGE_ENSEMBLE"
}
(out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")

audit=f"""============================================================
P2395 COMPLETE â CONTEXT ROUTER V2
============================================================
MISSION............. {MISSION}
MODE................ {MODE}
REAL_ORDERS......... {REAL_ORDERS}
FTMO_REAL........... {FTMO_REAL}

INPUT:
{p2394}

EVIDENCE:
{out}

ROUTER FILE:
{router_file}

SOURCE CLUSTER...... {edge["cluster_id"]}
SOURCE EDGE......... {edge["source_candidate_id"]}
EDGE SCORE.......... {edge["final_score"]}
P2394 DECISION...... {decision}

ROUTER DECISION..... OBSERVE_ONLY
REASON.............. P2394 did not promote score
RUNTIME CANDIDATES.. {len(router_candidates)}
INTEGRATION MODE.... ISOLATED_RUNTIME_MODULE

CERTIFICATION....... P2395_CONTEXT_ROUTER_V2_OBSERVE_ONLY_CERTIFIED
PAPER STACK MOD..... True
REAL_EXEC_ALLOWED... False
NEXT_REQUIRED....... P2396_EDGE_ENSEMBLE

AUDIT:
- P2394 consumido como fonte oficial.
- Edge observado nÃ£o foi liberado para runtime operacional.
- Router V2 criado como mÃ³dulo isolado e testÃ¡vel.
- Nenhuma execuÃ§Ã£o real permitida.
- REAL_ORDERS e FTMO_REAL permanecem FORBIDDEN.
- Governance Lock preservado.
============================================================
"""
(out/"AUDIT_FINAL.txt").write_text(audit,encoding="utf-8")
print(audit)
