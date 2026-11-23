import hashlib
import importlib.util
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "app/runtime/p2393_historical_provenance_gate.py"
spec = importlib.util.spec_from_file_location("p2393_gate", p)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def fixtures():
    best = dict(candidate_id="P2391_8149352397", dimensions="session+footprint+lifecycle+cycle_transition", key="US_AFTERNOON|LIQUIDITY_SWEEP_REVERSAL_DOWN|LIQUIDITY_REVERSAL_ENTRY|DISTRIBUTION->BALANCE", direction="BUY_PAPER", samples=152, passed_windows=4, pf=1.715719, winrate=59.210526, expectancy=0.139817, max_dd_r=4.158651, net_r=21.252145)
    k = "|".join(best[x] for x in ("dimensions", "key", "direction"))
    c = dict(best)
    c["source_candidate_id"] = c.pop("candidate_id")
    c.update(cluster_id="P2393_CLUSTER_"+hashlib.sha256(k.encode()).hexdigest()[:12].upper(), members=1, decision="PROMOTE_CLUSTER")
    flags = dict(mode="PAPER_ONLY", real_orders="FORBIDDEN", ftmo_real="FORBIDDEN", real_execution_allowed=False, paper_stack_modified=False)
    return dict(flags, best_promoted=best, promoted=1), dict(flags, best_cluster=c, clusters_created=1)

def test_valid_documents_not_e2e():
    assert gate.verify_p2393(*fixtures()) == (True, "HISTORICAL_DOCUMENTS_CONSISTENT_NOT_E2E_CERTIFIED")

def test_tampered_cluster_rejected():
    a,b=fixtures()
    b["best_cluster"]["expectancy"]=999
    assert gate.verify_p2393(a,b)[0] is False

def test_real_orders_rejected():
    a,b=fixtures()
    b["real_orders"]="ALLOWED"
    assert gate.verify_p2393(a,b)[0] is False

def test_cluster_id_rejected():
    a,b=fixtures()
    b["best_cluster"]["cluster_id"]="P2393_CLUSTER_FAKE"
    assert gate.verify_p2393(a,b)[0] is False
