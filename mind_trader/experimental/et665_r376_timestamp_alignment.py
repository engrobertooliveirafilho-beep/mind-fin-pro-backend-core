"""ET665.R376: timestamp-aligned PAPER trades before R375 walk-forward.

No timestamp inference. All strategies must contain identical, strictly ordered
event timestamps in each window; this is a research adapter, not real fills.
"""
from mind_trader.experimental.et665_r375_measured_walk_forward import evaluate_portfolio
from mind_trader.experimental.et665_r372_walk_forward_policy import decimal

def evaluate_timestamped_portfolio(strategies,max_abs_correlation="0.8"):
    if not isinstance(strategies,dict) or len(strategies)<2:
        raise ValueError("at least two strategies required")
    normalized={};reference=None
    for name,windows in sorted(strategies.items()):
        if not isinstance(name,str) or not name or not isinstance(windows,list) or len(windows)!=5:
            raise ValueError("invalid strategy windows")
        out=[];signature=[];seen=set();last=None
        for window in windows:
            if not isinstance(window,dict) or set(window)!={"window_id","trades"} or not isinstance(window["trades"],list):
                raise ValueError("invalid window schema")
            values=[]
            for trade in window["trades"]:
                if not isinstance(trade,dict) or set(trade)!={"ts","r"}:
                    raise ValueError("timestamp and R required")
                ts=trade["ts"]
                if type(ts) is not int or ts<0 or ts in seen or (last is not None and ts<=last):
                    raise ValueError("timestamps must be strictly increasing and unique")
                last=ts;seen.add(ts)
                values.append(str(decimal(trade["r"])))
                signature.append((window["window_id"],ts))
            out.append({"window_id":window["window_id"],"trades":values})
        if reference is None:reference=signature
        elif signature!=reference:raise ValueError("unaligned trade timestamps")
        normalized[name]=out
    result=evaluate_portfolio(normalized,max_abs_correlation)
    result["alignment"]="EXACT_TIMESTAMP_MATCH"
    result["historical_fills_verified"]=False
    result["strategy_promotion_authorized"]=False
    return result
