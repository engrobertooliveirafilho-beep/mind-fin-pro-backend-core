import json
import pytest
from app.runtime.p1633_confluence import reconcile, reconcile_file

def row(**kw):
    r=dict(asset='EURUSD',timeframe='H1',specialist_id='A1',family='momentum',profile='paper',deployment_score=40,confluence_score=50,opportunity_score=60,pattern_status='MINED_CANDIDATE',decision='WATCH_ONLY')
    r.update(kw)
    return r

def test_valid():
    r=reconcile([row()])
    assert r['candidates']==1 and r['order_send_allowed'] is False and r['promotion_allowed'] is False

@pytest.mark.parametrize('rows', [[],[{}],[row(specialist_id=' ')],[row(decision='PROMOTE')],[row(pattern_status='APPROVED')],[row(opportunity_score=True)],[row(opportunity_score='NaN')],[row(opportunity_score=101)],[row(),row(specialist_id=' a1 ')],[row(),row(specialist_id='A1')]])
def test_reject(rows):
    with pytest.raises(ValueError): reconcile(rows)

def test_file(tmp_path):
    p=tmp_path/'data.json'
    p.write_text(json.dumps([row()]))
    assert len(reconcile_file(p)['historical_sha256'])==64

def test_duplicate_json(tmp_path):
    p=tmp_path/'data.json'
    p.write_text('[{"asset":"A","asset":"B"}]')
    with pytest.raises(ValueError,match='duplicate JSON'): reconcile_file(p)

def test_empty(tmp_path):
    p=tmp_path/'data.json'
    p.write_bytes(b'')
    with pytest.raises(ValueError): reconcile_file(p)

def test_missing(tmp_path):
    with pytest.raises(ValueError): reconcile_file(tmp_path/'absent')

def test_nonfinite_json(tmp_path):
    p=tmp_path/'data.json'
    p.write_text('[NaN]')
    with pytest.raises(ValueError): reconcile_file(p)
