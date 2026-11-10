"""ET665.R368 isolated multi-strategy and portfolio PAPER backtest.

This adapter consumes independent predeclared strategy signals on the same
chronological bars. P2405 historical contract not yet located or integrated.
"""
from decimal import Decimal
from mind_trader.experimental.et665_r367_chronological_backtest import run_fixed_strategy,money

def portfolio(rows_by_strategy,weights,**costs):
    if not isinstance(rows_by_strategy,dict) or len(rows_by_strategy)<2 or not isinstance(weights,dict) or set(weights)!=set(rows_by_strategy):
        raise ValueError("invalid strategy portfolio")
    if any(not isinstance(k,str) or not k for k in weights):
        raise ValueError("invalid strategy id")
    w={k:money(v) for k,v in weights.items()}
    if sum(w.values())!=Decimal("1"):
        raise ValueError("weights must sum to one")
    results={k:run_fixed_strategy(v,**costs) for k,v in rows_by_strategy.items()}
    signatures=[tuple((r["ts"],r["open"],r["close"]) for r in rows) for rows in rows_by_strategy.values()]
    if any(x!=signatures[0] for x in signatures[1:]):
        raise ValueError("misaligned strategy price histories")
    combined={}
    for partition in ("train","validation","test"):
        net=sum((w[k]*Decimal(r["results"][partition]["net_return"]) for k,r in results.items()),Decimal(0))
        gross=sum((w[k]*Decimal(r["results"][partition]["gross_return"]) for k,r in results.items()),Decimal(0))
        combined[partition]={"weighted_net_return":str(net),"weighted_gross_return":str(gross),
                             "total_trades":sum(r["results"][partition]["trades"] for r in results.values())}
    return {"status":"processed","strategies":results,"portfolio":combined,
            "model":"weighted_sum_of_segment_returns_not_compounded",
            "real_orders":"FORBIDDEN","promotion_authorized":False,
            "historical_p2405_integrated":False}
