"""P1350 offline regime classifier; read-only, no trade execution."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

def classify(bars, *, min_bars=20, trend_threshold=Decimal('0.03'), vol_threshold=Decimal('0.025')):
    if not isinstance(bars, list) or len(bars) < min_bars or min_bars < 3:
        raise ValueError('insufficient history')
    prev = None
    prices = []
    normalized = []
    for b in bars:
        if not isinstance(b, dict) or not isinstance(b.get('timestamp'), str):
            raise ValueError('invalid bar')
        try:
            dt = datetime.fromisoformat(b['timestamp'].replace('Z', '+00:00'))
            o,h,l,c = (Decimal(str(b[k])) for k in ('open','high','low','close'))
        except (KeyError, ValueError, InvalidOperation, TypeError) as exc:
            raise ValueError('invalid OHLC') from exc
        if dt.tzinfo is None or (prev is not None and dt <= prev):
            raise ValueError('timestamps must be strictly chronological and timezone aware')
        if not all(v.is_finite() and v > 0 for v in (o,h,l,c)) or l > min(o,c) or h < max(o,c):
            raise ValueError('invalid OHLC bounds')
        prev = dt
        prices.append(c)
        normalized.append((dt.isoformat(),str(o),str(h),str(l),str(c)))
    returns = [prices[i] / prices[i-1] - 1 for i in range(1,len(prices))]
    mean = sum(returns, Decimal(0))/len(returns)
    variance = sum(((r-mean)**2 for r in returns), Decimal(0))/len(returns)
    volatility = variance.sqrt()
    trend = prices[-1]/prices[0]-1
    if volatility >= vol_threshold:
        regime = 'HIGH_VOLATILITY'
    elif trend >= trend_threshold:
        regime = 'TREND_UP'
    elif trend <= -trend_threshold:
        regime = 'TREND_DOWN'
    else:
        regime = 'RANGE'
    digest=sha256(json.dumps(normalized,separators=(',',':')).encode()).hexdigest()
    return {'regime':regime,'trend':str(trend),'volatility':str(volatility),'bars':len(bars),
            'source_sha256':digest,'status':'CLASSIFIED_OFFLINE','validated_out_of_sample':False,
            'order_send_allowed':False,'e2e_certified':False}
