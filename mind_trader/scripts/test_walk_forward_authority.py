import pytest
from mind_trader.app.validation.walk_forward_authority import walk_forward_authority

@pytest.mark.parametrize('value',[float('inf'),float('nan'),True,'2',-1])
def test_invalid(value):
    assert not walk_forward_authority([{'expectancy':1,'profit_factor':value}]*3)['passed']

def test_research_only():
    r=walk_forward_authority([{'expectancy':1,'profit_factor':2}]*3)
    assert r['passed'] and r['production']=='BLOCKED' and r['live']=='FORBIDDEN'

def test_missing():
    assert not walk_forward_authority([{'expectancy':1}]*3)['passed']
