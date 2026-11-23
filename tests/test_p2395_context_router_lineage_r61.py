from app.runtime.p2395_context_router_v2 import build_router

def test_historical_observe_score():
    r=build_router({"decision":"OBSERVE_SCORE","final_score":68.391266}).route({})
    assert not r.allowed and r.route=="OBSERVE_ONLY"

def test_context_missing():
    r=build_router({"decision":"PROMOTE_SCORE","final_score":80,"key":"A","direction":"BUY_PAPER"}).route({})
    assert not r.allowed and r.reason=="CONTEXT_MISMATCH"

def test_context_mismatch():
    r=build_router({"decision":"PROMOTE_SCORE","final_score":80,"key":"A","direction":"BUY_PAPER"}).route({"key":"B","direction":"BUY_PAPER"})
    assert not r.allowed and r.reason=="CONTEXT_MISMATCH"

def test_exact_paper_context():
    r=build_router({"decision":"PROMOTE_SCORE","final_score":80,"key":"A","direction":"BUY_PAPER"}).route({"key":"A","direction":"BUY_PAPER"})
    assert r.allowed and r.route=="PAPER_SIGNAL_CANDIDATE" and r.real_orders=="FORBIDDEN"

def test_invalid_score():
    r=build_router({"decision":"PROMOTE_SCORE","final_score":"not-a-number","key":"A","direction":"BUY_PAPER"}).route({"key":"A","direction":"BUY_PAPER"})
    assert not r.allowed and r.reason=="INVALID_EDGE_SCORE"
