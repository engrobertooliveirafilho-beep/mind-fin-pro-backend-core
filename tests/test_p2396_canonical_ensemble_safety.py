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


def test_historical_p2395_to_p2396_observe_only():
    from dataclasses import asdict
    from app.runtime.p2395_context_router_v2 import build_router
    scored = {"decision":"OBSERVE_SCORE","final_score":68.391266,"key":"US_AFTERNOON|LIQUIDITY_SWEEP_REVERSAL_DOWN|LIQUIDITY_REVERSAL_ENTRY|DISTRIBUTION->BALANCE","direction":"BUY_PAPER"}
    routed = build_router(scored).route({"key":scored["key"],"direction":"BUY_PAPER"})
    assert routed.allowed is False and routed.route == "OBSERVE_ONLY"
    decision = asdict(routed)
    decision["member_id"] = "P2391_8149352397"
    result = build_ensemble([decision],quorum=2).vote()
    assert (result.allowed,result.vote,result.reason,result.members,result.operational_members) == (False,"OBSERVE_ONLY","INSUFFICIENT_OPERATIONAL_QUORUM",1,0)
    assert result.real_orders == "FORBIDDEN" and result.ftmo_real == "FORBIDDEN"


def test_historical_p2396_to_p2397_offline_only():
    from app.runtime.p2397_meta_learning_offline import build_meta_learning
    ensemble = build_ensemble([v("P2391_8149352397",False)],quorum=2).vote()
    assert not ensemble.allowed and ensemble.vote == "OBSERVE_ONLY"
    hypotheses = [{"type":"DD_REDUCTION","paper_only":True}]
    decision = build_meta_learning({"decision":"OBSERVE_SCORE"},hypotheses).evaluate()
    assert decision.allowed_for_runtime is False
    assert decision.allowed_for_research is True
    assert decision.decision == "RESEARCH_ONLY" and decision.hypotheses == 1
    assert decision.real_orders == "FORBIDDEN" and decision.ftmo_real == "FORBIDDEN"
