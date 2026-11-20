import json
import pytest
from app.runtime.p402_shadow_safe import route_shadow,run

def edge(**changes):
    x=dict(job_id='e1',asset='XAUUSD',timeframe='M15',institutional_score=2.5)
    x.update(changes)
    return x

def test_watch():
    r=route_shadow([edge()],[])[0]
    assert r['shadow_action']=='SHADOW_WATCH' and r['order_sent'] is False and r['REAL_ORDERS']=='FORBIDDEN'

def test_open_position():
    assert route_shadow([edge()],[{'symbol':'XAUUSD'}])[0]['shadow_action']=='SHADOW_MONITOR_EXISTING_POSITION'

@pytest.mark.parametrize('changes',[{'institutional_score':float('nan')},{'institutional_score':float('inf')},{'institutional_score':True},{'job_id':''},{'asset':None},{'timeframe':None},{'REAL_ORDERS':'ALLOWED'}])
def test_reject_bad_edges(changes):
    with pytest.raises(ValueError):route_shadow([edge(**changes)],[])

def test_reject_duplicate():
    with pytest.raises(ValueError):route_shadow([edge(),edge()],[])

def test_reject_missing_positions():
    with pytest.raises(ValueError):route_shadow([edge()],None)

def test_reject_empty_edges():
    with pytest.raises(ValueError):route_shadow([],[])

def test_reject_invalid_position():
    with pytest.raises(ValueError):route_shadow([edge()],[{}])

def test_failclosed_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError):run(tmp_path/'missing.json',tmp_path/'positions.json',tmp_path/'out')
    assert not (tmp_path/'out').exists()

def test_write_shadow_only(tmp_path):
    src=tmp_path/'src.json';pos=tmp_path/'pos.json';out=tmp_path/'out'
    src.write_text(json.dumps([edge()]));pos.write_text('[]')
    result=run(src,pos,out)
    assert result['ORDER_SENT'] is False and json.loads((out/'p402_shadow_routes.json').read_text())[0]['FTMO_REAL']=='FORBIDDEN'
