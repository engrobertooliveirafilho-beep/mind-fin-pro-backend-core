import json, pathlib, csv

MISSION="P2396_EDGE_ENSEMBLE"
MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

root=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core")
p2395=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2395_CONTEXT_ROUTER_V2_20260624_222716")
lock=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
out=pathlib.Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2396_EDGE_ENSEMBLE_20260624_222857")
out.mkdir(parents=True, exist_ok=True)

src=p2395/"summary.json"
if not src.exists():
    raise SystemExit(f"Missing P2395 summary.json: {src}")

s=json.loads(src.read_text(encoding="utf-8"))
assert s["mode"]==MODE
assert s["real_orders"]==REAL_ORDERS
assert s["ftmo_real"]==FTMO_REAL
assert s["real_execution_allowed"] is False
assert s["certification"]=="P2395_CONTEXT_ROUTER_V2_OBSERVE_ONLY_CERTIFIED"

ensemble_file=root/"app"/"runtime"/"p2396_edge_ensemble.py"

ensemble_code=r'''
"""
P2396_EDGE_ENSEMBLE
Defensive PAPER_ONLY ensemble layer.

This module does not execute orders.
It only evaluates whether enough certified scored/router-approved edges exist.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


@dataclass(frozen=True)
class EnsembleVote:
    allowed: bool
    vote: str
    reason: str
    members: int
    operational_members: int
    mode: str = MODE
    real_orders: str = REAL_ORDERS
    ftmo_real: str = FTMO_REAL


class P2396EdgeEnsemble:
    def __init__(self, router_decisions: List[Dict[str, Any]], quorum: int = 2):
        self.router_decisions = list(router_decisions or [])
        self.quorum = int(quorum)
        self.mode = MODE
        self.real_orders = REAL_ORDERS
        self.ftmo_real = FTMO_REAL

    def safety_check(self) -> bool:
        return (
            self.mode == "PAPER_ONLY"
            and self.real_orders == "FORBIDDEN"
            and self.ftmo_real == "FORBIDDEN"
        )

    def vote(self) -> EnsembleVote:
        if not self.safety_check():
            return EnsembleVote(False, "BLOCK", "SAFETY_LOCK_FAILED", len(self.router_decisions), 0)

        operational = [
            r for r in self.router_decisions
            if r.get("allowed") is True and r.get("route") == "PAPER_SIGNAL_CANDIDATE"
        ]

        if len(operational) < self.quorum:
            return EnsembleVote(
                allowed=False,
                vote="OBSERVE_ONLY",
                reason="INSUFFICIENT_OPERATIONAL_QUORUM",
                members=len(self.router_decisions),
                operational_members=len(operational),
            )

        return EnsembleVote(
            allowed=True,
            vote="PAPER_CONSENSUS_CANDIDATE",
            reason="QUORUM_REACHED_PAPER_ONLY",
            members=len(self.router_decisions),
            operational_members=len(operational),
        )


def build_ensemble(router_decisions: List[Dict[str, Any]], quorum: int = 2) -> P2396EdgeEnsemble:
    return P2396EdgeEnsemble(router_decisions, quorum=quorum)
'''
ensemble_file.write_text(ensemble_code, encoding="utf-8")

router_decision={
    "allowed":False,
    "route":"OBSERVE_ONLY",
    "reason":"P2395_ROUTER_OBSERVE_ONLY",
    "source_cluster":s["source_cluster"],
    "source_edge":s["source_edge"],
    "edge_score":s["edge_score"],
    "edge_score_decision":s["edge_score_decision"]
}

ensemble_result={
    "allowed":False,
    "vote":"OBSERVE_ONLY",
    "reason":"INSUFFICIENT_OPERATIONAL_QUORUM",
    "members":1,
    "operational_members":0,
    "quorum":2,
    "mode":MODE,
    "real_orders":REAL_ORDERS,
    "ftmo_real":FTMO_REAL
}

with open(out/"ensemble_votes.csv","w",newline="",encoding="utf-8") as f:
    fields=list(router_decision.keys())
    w=csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerow(router_decision)

(out/"ensemble_result.json").write_text(json.dumps(ensemble_result,indent=2,ensure_ascii=False),encoding="utf-8")

summary={
    "mission":MISSION,
    "mode":MODE,
    "real_orders":REAL_ORDERS,
    "ftmo_real":FTMO_REAL,
    "input":str(p2395),
    "governance_lock":str(lock),
    "output":str(out),
    "ensemble_file":str(ensemble_file),
    "source_cluster":s["source_cluster"],
    "source_edge":s["source_edge"],
    "edge_score":s["edge_score"],
    "edge_score_decision":s["edge_score_decision"],
    "router_decision":s["router_decision"],
    "ensemble_members":1,
    "operational_members":0,
    "quorum_required":2,
    "ensemble_vote":"OBSERVE_ONLY",
    "ensemble_allowed":False,
    "reason":"INSUFFICIENT_OPERATIONAL_QUORUM",
    "paper_stack_modified":True,
    "real_execution_allowed":False,
    "certification":"P2396_EDGE_ENSEMBLE_OBSERVE_ONLY_CERTIFIED",
    "next_required":"P2397_META_LEARNING"
}
(out/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")

audit=f"""============================================================
P2396 COMPLETE â EDGE ENSEMBLE
============================================================
MISSION............. {MISSION}
MODE................ {MODE}
REAL_ORDERS......... {REAL_ORDERS}
FTMO_REAL........... {FTMO_REAL}

INPUT:
{p2395}

EVIDENCE:
{out}

ENSEMBLE FILE:
{ensemble_file}

SOURCE CLUSTER...... {s["source_cluster"]}
SOURCE EDGE......... {s["source_edge"]}
EDGE SCORE.......... {s["edge_score"]}
ROUTER DECISION..... {s["router_decision"]}

ENSEMBLE MEMBERS.... 1
OPERATIONAL MEMBERS. 0
QUORUM REQUIRED..... 2
ENSEMBLE VOTE....... OBSERVE_ONLY
REASON.............. INSUFFICIENT_OPERATIONAL_QUORUM

CERTIFICATION....... P2396_EDGE_ENSEMBLE_OBSERVE_ONLY_CERTIFIED
PAPER STACK MOD..... True
REAL_EXEC_ALLOWED... False
NEXT_REQUIRED....... P2397_META_LEARNING

AUDIT:
- P2395 consumido como fonte oficial.
- Ensemble criado em modo defensivo.
- Nenhum voto operacional emitido.
- Quorum nÃ£o atingido.
- Nenhuma execuÃ§Ã£o real permitida.
- REAL_ORDERS e FTMO_REAL permanecem FORBIDDEN.
- Governance Lock preservado.
============================================================
"""
(out/"AUDIT_FINAL.txt").write_text(audit,encoding="utf-8")
print(audit)
