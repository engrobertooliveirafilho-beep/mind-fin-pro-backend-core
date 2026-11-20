"""P1300 offline chronological split validation; no broker or order integration."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

def validate(bars, *, train=12, validation=4, test=4, spread='0.0002', slippage='0.0001', commission='0.0001'):
    if not isinstance(bars,list) or any(type(n) is not int or n<2 for n in (train,validation,test)) or len(bars)<train+validation+test:
        raise ValueError('insufficient chronological data')
    costs=[]
    for x in (spread,slippage,commission):
        try:d=Decimal(str(x))
        except (ValueError,TypeError,InvalidOperation) as exc:raise ValueError('invalid cost') from exc
        if not d.is_finite() or d<0:raise ValueError('invalid cost')
        costs.append(d)
    last=None;prices=[];serial=[]
    for bar in bars:
        if not isinstance(bar,dict) or not isinstance(bar.get('timestamp'),str):raise ValueError('invalid bar')
        try:
            t=datetime.fromisoformat(bar['timestamp'].replace('Z','+00:00'))
            o,h,l,c=(Decimal(str(bar[k])) for k in ('open','high','low','close'))
        except (KeyError,ValueError,TypeError,InvalidOperation) as exc:raise ValueError('invalid OHLC') from exc
        if t.tzinfo is None or (last is not None and t<=last):raise ValueError('nonchronological timestamp')
        if not all(v.is_finite() and v>0 for v in (o,h,l,c)) or l>min(o,c) or h<max(o,c):raise ValueError('invalid price')
        last=t;prices.append(c);serial.append((t.isoformat(),*[str(v) for v in (o,h,l,c)]))
    segments=[prices[:train],prices[train:train+validation],prices[train+validation:train+validation+test]]
    def pnl(segment):
        return str(sum((segment[i]/segment[i-1]-1-sum(costs) for i in range(1,len(segment))),Decimal(0)))
    return {'status':'OFFLINE_VALIDATION_ONLY','train_net_return':pnl(segments[0]),'validation_net_return':pnl(segments[1]),'test_net_return':pnl(segments[2]),'train_bars':train,'validation_bars':validation,'test_bars':test,'unused_bars':len(bars)-sum((train,validation,test)),'source_sha256':sha256(json.dumps(serial,separators=(',',':')).encode()).hexdigest(),'promotion_allowed':False,'order_send_allowed':False,'e2e_certified':False}
