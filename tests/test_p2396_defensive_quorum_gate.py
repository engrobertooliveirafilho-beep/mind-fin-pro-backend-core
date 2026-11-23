import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"app/runtime/p2396_defensive_quorum_gate.py"
s=importlib.util.spec_from_file_location("p2396_gate",p)
m=importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def test_original_observe_vote_blocked():
    v={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","allowed":False,"route":"OBSERVE_ONLY","edge_score_decision":"OBSERVE_SCORE"}
    assert m.validate_ensemble_vote([v])==(False,"INSUFFICIENT_OPERATIONAL_QUORUM")

def test_one_operational_vote_insufficient():
    v={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","allowed":True,"route":"PAPER_OPERATIONAL","edge_score_decision":"PROMOTE_SCORE"}
    assert m.validate_ensemble_vote([v])==(False,"INSUFFICIENT_OPERATIONAL_QUORUM")

def test_two_unverified_votes_still_blocked():
    v={"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","allowed":True,"route":"PAPER_OPERATIONAL","edge_score_decision":"PROMOTE_SCORE"}
    assert m.validate_ensemble_vote([v,v])==(False,"INDEPENDENT_ENSEMBLE_EVIDENCE_REQUIRED")

def test_real_orders_forbidden():
    v={"mode":"PAPER_ONLY","real_orders":"ALLOWED","ftmo_real":"FORBIDDEN"}
    assert m.validate_ensemble_vote([v])==(False,"EXECUTION_MODE_FORBIDDEN")
