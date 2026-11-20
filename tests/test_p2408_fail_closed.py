import copy
import pytest
from app.runtime.p2408_paper_runtime_integration_gated import build_runtime, runtime_allowed

POLICY=dict(mode="PAPER_ONLY",real_orders="FORBIDDEN",ftmo_real="FORBIDDEN",
            real_execution_allowed=False,allowed_symbol="GER40",
            allowed_sessions=["US_AFTERNOON"],allowed_regimes=["TREND_UP"],
            allowed_timeframes=["M15"],min_context_matches=3,
            min_weight_sum=.4,min_confidence=.62)
CONTEXT=dict(symbol="GER40",session="US_AFTERNOON",regime="TREND_UP",
             timeframe="M15",direction="BUY_PAPER")
MEMBERS=[dict(session="US_AFTERNOON",regime="TREND_UP",timeframe="M15",
              direction="BUY_PAPER",ensemble_weight=.25) for _ in range(3)]

def run(context=None,policy=None,members=None):
    return build_runtime(copy.deepcopy(MEMBERS if members is None else members),
                         copy.deepcopy(POLICY if policy is None else policy)).dispatch(
                             copy.deepcopy(CONTEXT if context is None else context))

def test_valid_paper():
    r=run()
    assert r["allowed"] is True and r["route"]=="PAPER_SIGNAL_CANDIDATE"
    assert r["real_execution_allowed"] is False and runtime_allowed() is False

@pytest.mark.parametrize("field,value",[
    ("mode","REAL"),("real_orders","ALLOWED"),("ftmo_real","ALLOWED"),
    ("real_execution_allowed",True),("direction","BUY_REAL"),("session","UNKNOWN"),
    ("regime","UNKNOWN"),("timeframe","D1"),("symbol","XAUUSD"),
    ("direction",None),("session",None)])
def test_bad_context(field,value):
    ctx=dict(CONTEXT);ctx[field]=value
    assert run(context=ctx)["allowed"] is False

@pytest.mark.parametrize("field,value",[
    ("mode","REAL"),("real_orders","ALLOWED"),("ftmo_real","ALLOWED"),
    ("real_execution_allowed",True),("allowed_sessions",None),
    ("min_context_matches","NaN"),("min_confidence",float("nan")),
    ("min_weight_sum",float("inf"))])
def test_bad_policy(field,value):
    p=dict(POLICY);p[field]=value
    assert run(policy=p)["allowed"] is False

@pytest.mark.parametrize("weight",[float("nan"),float("inf"),-1,1.1,"invalid",None,True])
def test_bad_weights(weight):
    m=copy.deepcopy(MEMBERS);m[0]["ensemble_weight"]=weight
    assert run(members=m)["allowed"] is False

def test_malformed():
    assert run(members=[])["allowed"] is False
    assert run(members=[None])["allowed"] is False
    assert build_runtime(MEMBERS,POLICY).dispatch(None)["allowed"] is False

def test_quorum_confidence():
    assert run(members=MEMBERS[:2])["allowed"] is False
    m=copy.deepcopy(MEMBERS)
    for row in m:row["ensemble_weight"]=.01
    assert run(members=m)["allowed"] is False
