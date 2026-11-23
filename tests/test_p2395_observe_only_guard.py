import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"app/runtime/p2395_observe_only_guard.py"
spec=importlib.util.spec_from_file_location("p2395_guard",p)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def test_observed_score_rejected():
    assert gate.validate_p2395_routing({"decision":"OBSERVE_SCORE","cluster_id":"c"},{"cluster_id":"c","mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"}) == (False,"P2394_NOT_PROMOTED_OBSERVE_ONLY")

def test_unverified_promoted_score_still_rejected():
    assert gate.validate_p2395_routing({"decision":"PROMOTE_SCORE","cluster_id":"c"},{"cluster_id":"c","mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"}) == (False,"INDEPENDENT_ROUTER_INTEGRATION_NOT_CERTIFIED")

def test_real_orders_rejected():
    assert gate.validate_p2395_routing({"decision":"PROMOTE_SCORE","cluster_id":"c"},{"cluster_id":"c","mode":"PAPER_ONLY","real_orders":"ALLOWED","ftmo_real":"FORBIDDEN"}) == (False,"EXECUTION_MODE_FORBIDDEN")
