import pytest
from app.runtime.p2308_non_ger40_candidate_gate import reconcile

@pytest.fixture
def evidence():
    syms=('EURUSD','GBPUSD','USDJPY','USDCHF','USDCAD','XAUUSD','US100','US500','UK100','JP225')
    summary={'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN','total_non_ger40_candidates':'120960'}
    rules={'engine_required':'P2296C_REAL_EXIT_ENGINE_ONLY','dedup_required':'TRUE','wf_segmented_required':'TRUE','stress_required':'TRUE'}
    rows=[{'target_symbol':s,'candidate_rows':'12096','batches_with_symbol':'26' if s=='USDCHF' else '25','status':'CANDIDATES_FOUND'} for s in syms]
    return summary,rows,rules

def test_historical(evidence):
    assert reconcile(*evidence)['tested_edges']==0

@pytest.mark.parametrize('field,bad',[('mode','LIVE'),('real_orders','ALLOWED'),('ftmo_real','ALLOWED'),('total_non_ger40_candidates','120959')])
def test_summary_fail(evidence,field,bad):
    evidence[0][field]=bad
    with pytest.raises(ValueError): reconcile(*evidence)

@pytest.mark.parametrize('field,bad',[('engine_required','P2286D'),('dedup_required','FALSE'),('wf_segmented_required','FALSE'),('stress_required','FALSE')])
def test_rule_fail(evidence,field,bad):
    evidence[2][field]=bad
    with pytest.raises(ValueError): reconcile(*evidence)

def test_duplicate_symbol(evidence):
    evidence[1][1]['target_symbol']='EURUSD'
    with pytest.raises(ValueError):reconcile(*evidence)

def test_false_backtest_status(evidence):
    evidence[1][0]['status']='BACKTEST_PASS'
    with pytest.raises(ValueError):reconcile(*evidence)
