import pytest
from app.runtime.p2360_mae_mfe_real_capture_engine import calculate_mae_mfe
@pytest.mark.parametrize('side,path,exit_price,expected',[('BUY',[11,12],13,(0,3)),('SELL',[11,12],13,(-3,0)),('BUY',[9,12],11,(-1,2)),('SELL',[9,12],11,(-2,1))])
def test_bounds(side,path,exit_price,expected):
    r=calculate_mae_mfe(dict(entry_price=10,side=side,exit_price=exit_price),path)
    assert (r['mae'],r['mfe'])==expected
@pytest.mark.parametrize('price',[0,-1,float('inf'),float('nan'),True])
def test_invalid(price):
    with pytest.raises(ValueError): calculate_mae_mfe(dict(entry_price=10,side='BUY'),[price])
def test_side():
    with pytest.raises(ValueError): calculate_mae_mfe(dict(entry_price=10,side='HOLD'),[11])
