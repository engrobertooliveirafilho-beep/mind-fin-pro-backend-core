import copy
import pytest
from app.runtime.p2298_paper_decision_gate import reconcile_decision, REQUIRED_RESTRICTIONS

@pytest.fixture
def decision():
    return {'decision':'APPROVE_FOR_PAPER_WATCH_ONLY','mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN','legacy_engine':'INVALIDATED','valid_engine':'P2296C_REAL_EXIT_ENGINE','restrictions':list(REQUIRED_RESTRICTIONS)}

@pytest.fixture
def candidates():
    return [dict(symbol='GER40',timeframe='H1',mode='PAPER_ONLY',real_orders='FORBIDDEN',final_status='FINAL_APPROVED',segments_passed=3,seg1_pf=1.3627,seg2_pf=2.6884,seg3_pf=.844,seg4_pf=1.2031) for _ in range(4)]

def test_historical_4_same_metrics_not_four_independent(decision,candidates):
    r=reconcile_decision(decision,candidates)
    assert r['candidates']==4 and r['distinct_metric_signatures']==1 and r['independent_edges_certified']==0 and not r['e2e_certified']

@pytest.mark.parametrize('key,bad', [('mode','REAL'),('real_orders','ALLOWED'),('ftmo_real','ALLOWED'),('legacy_engine','VALID'),('valid_engine','UNKNOWN'),('decision','APPROVE_REAL')])
def test_unsafe_decision_rejected(decision,candidates,key,bad):
    decision[key]=bad
    with pytest.raises(ValueError,match='P2298_UNSAFE_DECISION'): reconcile_decision(decision,candidates)

def test_missing_stress_gate_rejected(decision,candidates):
    decision['restrictions'].remove('MONTE_CARLO_REQUIRED')
    with pytest.raises(ValueError,match='P2298_UNSAFE_DECISION'): reconcile_decision(decision,candidates)

@pytest.mark.parametrize('key,bad', [('symbol','EURUSD'),('real_orders','ALLOWED'),('final_status','FINAL_REJECTED')])
def test_candidate_fail_closed(decision,candidates,key,bad):
    candidates[0][key]=bad
    with pytest.raises(ValueError,match='P2298_UNAUTHORIZED_CANDIDATE'): reconcile_decision(decision,candidates)

@pytest.mark.parametrize('bad', [float('nan'),float('inf'),-1,True])
def test_invalid_pf_rejected(decision,candidates,bad):
    candidates[0]['seg1_pf']=bad
    with pytest.raises(ValueError,match='P2298_INVALID_METRICS'): reconcile_decision(decision,candidates)

def test_segment_mismatch_rejected(decision,candidates):
    candidates[0]['segments_passed']=4
    with pytest.raises(ValueError,match='P2298_INCONSISTENT_SEGMENTS'): reconcile_decision(decision,candidates)
