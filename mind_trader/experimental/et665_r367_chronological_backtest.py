"""ET665.R367 — isolated chronological PAPER backtest primitives.

No external data, brokers, optimization, production or strategy promotion.
Input bars are already chronological OHLC observations. The strategy is a
predeclared fixed-position signal; signals are shifted by one bar to prevent
same-bar execution and close-price lookahead.
"""
from decimal import Decimal,InvalidOperation

def money(v):
    if isinstance(v,bool) or not isinstance(v,(str,int)):
        raise ValueError("invalid numeric type")
    try: d=Decimal(str(v))
    except (InvalidOperation,ValueError) as exc: raise ValueError("invalid number") from exc
    if not d.is_finite() or d<0: raise ValueError("invalid nonnegative number")
    return d

def split_chronological(rows,train=6,validation=2,test=2):
    if not isinstance(rows,list) or len(rows)<train+validation+test or min(train,validation,test)<2:
        raise ValueError("insufficient chronological data")
    if train+validation+test!=len(rows):
        raise ValueError("all rows must be allocated")
    timestamps=[]
    for r in rows:
        if not isinstance(r,dict) or set(r)!={"ts","open","close","signal"}:
            raise ValueError("invalid bar schema")
        if not isinstance(r["ts"],int) or isinstance(r["ts"],bool):
            raise ValueError("invalid timestamp")
        op,cl=money(r["open"]),money(r["close"])
        if op<=0 or cl<=0 or r["signal"] not in (-1,0,1) or isinstance(r["signal"],bool):
            raise ValueError("invalid bar")
        timestamps.append(r["ts"])
    if timestamps!=sorted(set(timestamps)):
        raise ValueError("timestamps not strictly increasing")
    a=rows[:train];b=rows[train:train+validation];c=rows[train+validation:]
    return {"train":a,"validation":b,"test":c}

def backtest_segment(rows,spread_bps="0",slippage_bps="0",commission_bps="0"):
    """Use only prior-bar signal; first bar cannot trade across a split boundary."""
    costs=sum((money(spread_bps),money(slippage_bps),money(commission_bps)),Decimal(0))
    if costs>=Decimal(10000):
        raise ValueError("unreasonable costs")
    gross=Decimal(0);net=Decimal(0);trades=0
    for previous,current in zip(rows,rows[1:]):
        signal=previous["signal"]
        if signal==0:continue
        entry=money(current["open"]);exit_=money(current["close"])
        if entry<=0:raise ValueError("invalid entry")
        pnl=Decimal(signal)*(exit_-entry)/entry
        gross+=pnl
        net+=pnl-costs/Decimal(10000)
        trades+=1
    return {"trades":trades,"gross_return":str(gross),"net_return":str(net),
            "cost_bps":str(costs),"paper_only":True,"promotion_authorized":False}

def run_fixed_strategy(rows,train=6,validation=2,test=2,**costs):
    partitions=split_chronological(rows,train,validation,test)
    return {"partitions":{k:{"start":v[0]["ts"],"end":v[-1]["ts"],"count":len(v)}
                           for k,v in partitions.items()},
            "results":{k:backtest_segment(v,**costs) for k,v in partitions.items()},
            "real_orders":"FORBIDDEN","strategy_promotion":"FORBIDDEN",
            "historical_p2405_integrated":False}
