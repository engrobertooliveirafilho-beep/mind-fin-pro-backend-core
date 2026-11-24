import ast
from pathlib import Path
import pytest
source=ast.parse((Path(__file__).resolve().parents[1]/'app/runtime/p2362_full_signal_decision_pipeline.py').read_text())
node=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='decide_signal')
@pytest.mark.parametrize('edge,allowed,lot,expected',[('UNKNOWN_CONTEXT_EDGE',True,.01,False),('TRENDING_BREAKOUT',True,.01,True),('TRENDING_BREAKOUT',False,.01,False),('TRENDING_BREAKOUT',True,0,False),('TRENDING_BREAKOUT','True',.01,False)])
def test_gate(edge,allowed,lot,expected):
    ns={'classify_context_edge':lambda c:{'edge_type':edge},'institutional_targets':lambda c:{'approved':True,'rr':3},'precheck_before_mt5_emit':lambda s,c:{'emit_allowed':allowed},'dynamic_paper_lot':lambda c:{'recommended_paper_lot':lot}}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'pipeline.py','exec'),ns)
    r=ns['decide_signal']({}, {})
    assert (r['final_decision']=='EMIT_TO_MT5_PAPER') is expected
    assert r['paper_lot']==(lot if expected else 0)
    assert r['real_orders']=='FORBIDDEN'
