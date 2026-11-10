"""ET665.R373: derive P2405F metrics from immutable PAPER trade returns.

Returns are R multiples, not currency; no broker, fills or promotion.
"""
from decimal import Decimal
from mind_trader.experimental.et665_r372_walk_forward_policy import decimal,evaluate

def metrics(trades):
    if not isinstance(trades,list) or not trades:
        raise ValueError("nonempty trade list required")
    values=[decimal(x) for x in trades]
    wins=[v for v in values if v>0]
    losses=[v for v in values if v<0]
    gross_profit=sum(wins,Decimal(0))
    gross_loss=-sum(losses,Decimal(0))
    pf=(gross_profit/gross_loss) if gross_loss else (Decimal("999999999") if gross_profit else Decimal(0))
    equity=Decimal(0);peak=Decimal(0);max_dd=Decimal(0)
    for v in values:
        equity+=v;peak=max(peak,equity);max_dd=max(max_dd,peak-equity)
    return {"samples":len(values),"pf":str(pf),
            "winrate":str(Decimal(100)*len(wins)/len(values)),
            "expectancy":str(sum(values,Decimal(0))/len(values)),
            "max_dd_r":str(max_dd)}

def evaluate_trades(windows,correlation_checked):
    if not isinstance(windows,list) or len(windows)!=5:
        raise ValueError("exactly five windows required")
    calculated=[]
    for w in windows:
        if not isinstance(w,dict) or set(w)!={"window_id","trades"}:
            raise ValueError("invalid trade window")
        calculated.append({"window_id":w["window_id"],**metrics(w["trades"])})
    result=evaluate(calculated,correlation_checked)
    result["source"]="PAPER_R_MULTIPLES_NOT_VERIFIED_FILLS"
    result["trade_metrics"]=calculated
    result["historical_fills_verified"]=False
    result["strategy_promotion_authorized"]=False
    return result
