from app.runtime.p2396_edge_ensemble import build_ensemble

def v(member, allowed=True):
    return {"member_id":member,"allowed":allowed,"route":"PAPER_SIGNAL_CANDIDATE","mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"}

def test_historical_observe_only():
    r=build_ensemble([v("historical",False)]).vote()
    assert not r.allowed and r.reason=="INSUFFICIENT_OPERATIONAL_QUORUM"

def test_duplicate_member_rejected():
    r=build_ensemble([v("a"),v("a")]).vote()
    assert not r.allowed and r.reason=="DUPLICATE_MEMBER"

def test_quorum_not_runtime_authority():
    r=build_ensemble([v("a"),v("b")]).vote()
    assert not r.allowed and r.reason=="INDEPENDENT_ENSEMBLE_EVIDENCE_REQUIRED"

def test_unsafe_router_flags():
    x=v("a");x["real_orders"]="ALLOWED"
    r=build_ensemble([x]).vote()
    assert not r.allowed and r.reason=="UNSAFE_ROUTER_DECISION"

def test_invalid_quorum():
    r=build_ensemble([v("a")],quorum=0).vote()
    assert not r.allowed and r.reason=="INVALID_QUORUM"
