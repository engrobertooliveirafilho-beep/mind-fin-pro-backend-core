from adapter import preflight
from integration_gate import evaluate
from paper_order_dispatch_guard import evaluate_paper_intent

ORDER = {'mode':'PAPER','symbol':'EURUSD','risk_amount':'50'}
STATE = {'mode':'PAPER','authority_verified':True,'risk_guard_wired':True,'kill_switch':False,'force_no_trade':False,'initial_balance':'10000','equity':'10000','day_start_equity':'10000','open_positions':0,'correlated_positions':0}

def test_actual_r6_evidence_denies_even_with_positive_self_attested_state():
    result=evaluate_paper_intent(ORDER,STATE,preflight=preflight(),integration=evaluate())
    assert result['approved'] is False
    assert result['reason']=='INTEGRATION_NOT_CERTIFIED'
    assert result['real_orders_authorized'] is False

def test_missing_gate_denies():
    assert not evaluate_paper_intent(ORDER,STATE,preflight=None,integration={})['approved']

def test_forged_preflight_without_verified_join_denies():
    p={'status':'PAPER_DISPATCH_CERTIFIED','missing_phases':[],'findings':[]}
    i={'status':'PAPER_DISPATCH_CERTIFIED','canonical_runtime_verified':True,'s20_s21_join_verified':False,'long_run_certified':True}
    assert not evaluate_paper_intent(ORDER,STATE,preflight=p,integration=i)['approved']

def test_forged_positive_gates_still_require_risk_guard():
    p={'status':'PAPER_DISPATCH_CERTIFIED','missing_phases':[],'findings':[]}
    i={'status':'PAPER_DISPATCH_CERTIFIED','canonical_runtime_verified':True,'s20_s21_join_verified':True,'long_run_certified':True}
    assert not evaluate_paper_intent({**ORDER,'mode':'LIVE'},STATE,preflight=p,integration=i)['approved']
    assert not evaluate_paper_intent(ORDER,{**STATE,'kill_switch':True},preflight=p,integration=i)['approved']


def test_forged_all_green_reports_cannot_authorize():
    forged = {'status': 'PAPER_DISPATCH_CERTIFIED', 'canonical_runtime_verified': True,
              's20_s21_join_verified': True, 'long_run_certified': True,
              'missing_phases': [], 'findings': []}
    decision = evaluate_paper_intent(ORDER, STATE, preflight=forged, integration=forged)
    assert decision['approved'] is False
    assert decision['real_orders_authorized'] is False
