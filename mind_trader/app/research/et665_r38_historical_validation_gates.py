"""ET665 R38: research-only hard gates for recovered P2357/P2358/P2359.

No broker imports, runtime promotion or order routing. Historical outputs are
untrusted input. This is a new guarded adapter, not a certification of originals.
"""
import math

def _num(x):
    return type(x) in (int, float) and math.isfinite(x)

def _nonneg(x):
    return _num(x) and x >= 0

def _block(reason):
    return {"decision":"REJECT_RESEARCH","reason":reason,"runtime_allowed":False,"real_orders":"FORBIDDEN"}

def walk_forward(windows):
    if not isinstance(windows,list) or len(windows)<3:
        return _block("INSUFFICIENT_WINDOWS")
    prev_end=None
    for w in windows:
        if not isinstance(w,dict):
            return _block("INVALID_WINDOW")
        keys=("train_start","train_end","test_start","test_end")
        if not all(isinstance(w.get(k),str) and w[k] for k in keys):
            return _block("MISSING_CHRONOLOGY")
        if not (w["train_start"] < w["train_end"] < w["test_start"] < w["test_end"]):
            return _block("LEAKAGE_OR_OVERLAP")
        if prev_end is not None and w["test_start"] <= prev_end:
            return _block("OVERLAPPING_TEST_WINDOWS")
        prev_end=w["test_end"]
        for k in ("train_pf","test_pf","test_payoff","test_drawdown"):
            if not _nonneg(w.get(k)):
                return _block("INVALID_METRICS")
        if type(w.get("test_trades")) is not int or w["test_trades"]<30:
            return _block("INSUFFICIENT_TRADES")
        degradation=max(0,(w["train_pf"]-w["test_pf"])/w["train_pf"]) if w["train_pf"] else 1
        if w["test_pf"]<1.5 or w["test_payoff"]<3 or w["test_drawdown"]>10 or degradation>0.35:
            return _block("WEAK_OUT_OF_SAMPLE")
    return {"decision":"RESEARCH_REVIEW_ONLY","windows":len(windows),"runtime_allowed":False,"real_orders":"FORBIDDEN"}

def anti_overfit(metrics):
    if not isinstance(metrics,dict) or metrics.get("source_verified") is not True or metrics.get("out_of_sample_verified") is not True:
        return _block("UNVERIFIED_PROVENANCE")
    limits={"symbols_tested":3,"years_tested":3,"regimes_tested":3}
    for k,v in limits.items():
        if type(metrics.get(k)) is not int or metrics[k]<v:
            return _block("INSUFFICIENT_COVERAGE")
    for k in ("out_of_sample_profit_factor","out_of_sample_payoff","out_of_sample_expectancy","max_drawdown","parameter_sensitivity"):
        if not _num(metrics.get(k)):
            return _block("INVALID_METRICS")
    if (metrics["out_of_sample_profit_factor"]<1.5 or metrics["out_of_sample_payoff"]<3
        or metrics["out_of_sample_expectancy"]<=0 or not _nonneg(metrics["max_drawdown"])
        or metrics["max_drawdown"]>10 or not _nonneg(metrics["parameter_sensitivity"])
        or metrics["parameter_sensitivity"]>35):
        return _block("OVERFIT_OR_WEAK")
    return {"decision":"RESEARCH_REVIEW_ONLY","runtime_allowed":False,"real_orders":"FORBIDDEN"}

def currency_exposure(trades, candidate):
    pairs={"EURUSD":("EUR","USD"),"GBPUSD":("GBP","USD"),
           "AUDUSD":("AUD","USD"),"NZDUSD":("NZD","USD"),
           "USDJPY":("USD","JPY"),"USDCHF":("USD","CHF"),"USDCAD":("USD","CAD")}
    if not isinstance(trades,list) or not isinstance(candidate,dict):
        return _block("INVALID_INPUT")
    totals={}
    for t in trades+[candidate]:
        if not isinstance(t,dict) or t.get("symbol") not in pairs or t.get("side") not in ("BUY","SELL") or not _num(t.get("lot")) or t["lot"]<=0:
            return _block("UNKNOWN_ASSET_OR_UNITS")
        base,quote=pairs[t["symbol"]]
        sign=1 if t["side"]=="BUY" else -1
        totals[base]=totals.get(base,0)+sign*t["lot"]
        totals[quote]=totals.get(quote,0)-sign*t["lot"]
    if any(abs(v)>=0.03-1e-12 for v in totals.values()):
        return _block("CURRENCY_CONCENTRATION")
    return {"decision":"RESEARCH_REVIEW_ONLY","exposure":totals,"runtime_allowed":False,"real_orders":"FORBIDDEN"}
