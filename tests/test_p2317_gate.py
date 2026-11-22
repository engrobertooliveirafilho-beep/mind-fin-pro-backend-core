import pytest
from app.runtime.p2317_gate import reconcile
S='GER40,BUY,0.01,P2316_34f0bb1186de,2026-06-22T14:47:30'
def sample():
    a={'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN','exists_after_write':'True','order_line':S}
    b={'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN','signal_exists':'True','signal_content':S,'consumption_status':'PARSED_BUT_FILE_STILL_PRESENT'}
    return a,b
def test_historical():
    r=reconcile(*sample());assert r['orders_authorized']==0 and not r['terminal_read_proven']
@pytest.mark.parametrize('index,key,value',[(0,'mode','LIVE'),(1,'mode','LIVE'),(0,'real_orders','ALLOWED'),(1,'ftmo_real','ALLOWED'),(0,'exists_after_write','False'),(1,'signal_exists','False'),(1,'signal_content','GER40,SELL,0.01,P2316_34f0bb1186de,2026-06-22T14:47:30'),(1,'consumption_status','CONSUMED'),(0,'order_line','EURUSD,BUY,0.01,P2316_34f0bb1186de,2026-06-22T14:47:30')])
def test_reject(index,key,value):
    e=list(sample());e[index][key]=value
    with pytest.raises(ValueError):reconcile(*e)
