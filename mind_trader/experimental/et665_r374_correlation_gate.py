"""ET665.R374: fail-closed cross-strategy correlation gate on PAPER R returns.

This checks a research portfolio only, not official P2405F certification.
"""
from decimal import Decimal
from itertools import combinations
from mind_trader.experimental.et665_r372_walk_forward_policy import decimal
from mind_trader.experimental.et665_r373_trade_metric_adapter import evaluate_trades

def correlation(a,b):
    if len(a)!=len(b) or len(a)<3:
        raise ValueError("aligned series with at least three observations required")
    x=[decimal(v) for v in a];y=[decimal(v) for v in b]
    n=Decimal(len(x));mx=sum(x)/n;my=sum(y)/n
    vx=sum((v-mx)**2 for v in x);vy=sum((v-my)**2 for v in y)
    if vx==0 or vy==0:
        raise ValueError("zero variance correlation undefined")
    return sum((u-mx)*(v-my) for u,v in zip(x,y))/(vx*vy).sqrt()

def assess(strategies,max_abs_correlation="0.8"):
    if not isinstance(strategies,dict) or len(strategies)<2:
        raise ValueError("at least two strategies required")
    threshold=decimal(max_abs_correlation)
    if not Decimal(0)<=threshold<Decimal(1):
        raise ValueError("invalid correlation threshold")
    names=sorted(strategies)
    for name in names:
        if not isinstance(name,str) or not name or not isinstance(strategies[name],list):
            raise ValueError("invalid strategy")
    length=len(strategies[names[0]])
    if length<3 or any(len(strategies[n])!=length for n in names):
        raise ValueError("misaligned strategy lengths")
    pairs=[]
    for a,b in combinations(names,2):
        r=correlation(strategies[a],strategies[b])
        pairs.append({"a":a,"b":b,"correlation":str(r),"pass":abs(r)<=threshold})
    return {"status":"PASS" if all(p["pass"] for p in pairs) else "BLOCKED",
            "pairs":pairs,"threshold":str(threshold),
            "strategy_promotion_authorized":False,"real_orders":"FORBIDDEN"}
