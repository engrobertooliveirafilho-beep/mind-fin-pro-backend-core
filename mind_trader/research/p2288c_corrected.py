"""P2288C corrected research-only evaluator. No broker connectivity or live orders.

Deliberately distinct from the immutable historical executor. Results are NOT
comparable with its cost-free, terminal-position-open walk-forward results.
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

FIELDS = ('symbol','timeframe','strategy','session_filter','volatility_filter','spread_filter','trend_filter')
REQUIRED = ('time','open','close','session','volatility_state','spread_state','trend_9_21','trend_21_55','trend_55_200')
STRATEGIES = {'SESSION_TREND','TREND_PULLBACK','VOL_BREAKOUT'}
TRENDS = {'ANY','trend_9_21','trend_21_55','trend_55_200'}


def load_strict(path: Path):
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or any(k not in reader.fieldnames for k in REQUIRED):
            raise ValueError('Missing required market-data columns')
        rows=[]
        for line,r in enumerate(reader,2):
            try:
                if any(r[k] is None or not r[k].strip() for k in REQUIRED):
                    raise ValueError('empty required field')
                r['open']=float(r['open']);r['close']=float(r['close'])
                if not (0<r['open']<float('inf') and 0<r['close']<float('inf')):
                    raise ValueError('invalid price')
                rows.append(r)
            except (ValueError,TypeError,KeyError) as e:
                raise ValueError(f'Malformed candle at line {line}: {e}') from e
    return rows


def unique_candidates(rows):
    groups=defaultdict(list)
    for n,r in enumerate(rows,1):
        if r.get('strategy') not in STRATEGIES or r.get('trend_filter') not in TRENDS:
            raise ValueError(f'Invalid strategy/filter at candidate {n}')
        if r.get('mode')!='PAPER_ONLY' or r.get('real_orders')!='FORBIDDEN':
            raise ValueError(f'Unsafe candidate {n}')
        groups[tuple(r[k] for k in FIELDS)].append(n)
    return groups


def passes(r,q):
    for key,col in [('session_filter','session'),('volatility_filter','volatility_state'),('spread_filter','spread_state')]:
        if q[key]!='ANY' and q[key]!=r[col]:return False
    return q['trend_filter']=='ANY' or r[q['trend_filter']]=='UP'


def signal(r,q):
    if not passes(r,q):return None
    strategy=q['strategy']
    if strategy=='SESSION_TREND' and r['session'] in ('LONDON','NY'):
        return {'UP':'BUY','DOWN':'SELL'}.get(r['trend_9_21'])
    if strategy=='TREND_PULLBACK' and q['trend_filter']!='ANY':
        if r[q['trend_filter']]=='UP' and r['close']>r['open']:return 'BUY'
        if r[q['trend_filter']]=='DOWN' and r['close']<r['open']:return 'SELL'
    if strategy=='VOL_BREAKOUT' and r['volatility_state']=='HIGH':
        if r['close']>r['open']:return 'BUY'
        if r['close']<r['open']:return 'SELL'
    return None


def backtest(rows,q,roundtrip_cost,close_terminal=True):
    """Costs are nonnegative PRICE UNITS per closed round trip, not pips or cash.
    Terminal close at final candle close. Segment boundaries reset exposure.
    """
    if roundtrip_cost is None or not 0<=roundtrip_cost<float('inf'):
        raise ValueError('Explicit finite nonnegative roundtrip_cost required')
    if not close_terminal:raise ValueError('Terminal closure required')
    pos=None;entry=None;trades=[]
    for i in range(1,len(rows)-1):
        s=signal(rows[i],q)
        if s is None:continue
        price=rows[i+1]['open']
        if pos is not None:
            trades.append(((price-entry) if pos=='BUY' else (entry-price))-roundtrip_cost)
        pos=s;entry=price
    if pos is not None:
        price=rows[-1]['close']
        trades.append(((price-entry) if pos=='BUY' else (entry-price))-roundtrip_cost)
    wins=sum(x for x in trades if x>0)
    losses=-sum(x for x in trades if x<0)
    pf=(wins/losses if losses else (float('inf') if wins else 0.0)) if len(trades)>=10 else 0.0
    return {'trades':len(trades),'pf':pf,'netprofit':sum(trades)}


def evaluate(candidates,datasets,cost_by_symbol):
    """No I/O except provided data; no approval if a cost model is missing."""
    groups=unique_candidates(candidates)
    outputs=[]
    for key,indices in groups.items():
        q=candidates[indices[0]-1];symbol=q['symbol'];tf=q['timeframe']
        if (symbol,tf) not in datasets or symbol not in cost_by_symbol:
            raise ValueError(f'Missing data or cost for {symbol}/{tf}')
        rows=datasets[(symbol,tf)]
        if len(rows)<1000:raise ValueError(f'Insufficient data {symbol}/{tf}')
        step=len(rows)//4
        parts=[backtest(rows[i*step:((i+1)*step if i<3 else len(rows))],q,cost_by_symbol[symbol]) for i in range(4)]
        passed=sum(p['pf']>=1.15 and p['netprofit']>0 and p['trades']>=10 for p in parts)
        outputs.append({'candidate_indices':indices,'segments':parts,'segments_passed':passed,
                        'status':'RESEARCH_WATCHLIST' if passed>=2 else 'RESEARCH_REJECTED',
                        'mode':'PAPER_ONLY','real_orders':'FORBIDDEN','financial_certified':False})
    return outputs
