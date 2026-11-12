"""ET665.R40: offline research-only guards. No broker imports or runtime promotion."""
from __future__ import annotations
from datetime import datetime
from math import isfinite

PAPER_ONLY = True
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"
PROMOTION_ALLOWED = False
FX_BASE = {"EURUSD": ("EUR","USD"),"GBPUSD":("GBP","USD"),"AUDUSD":("AUD","USD"),"NZDUSD":("NZD","USD"),"USDJPY":("USD","JPY"),"USDCHF":("USD","CHF"),"USDCAD":("USD","CAD")}

class ResearchRejected(ValueError):
    pass

def finite_number(value, name, *, positive=False, nonnegative=False):
    if isinstance(value, bool) or value is None:
        raise ResearchRejected(name + ": missing/invalid")
    try:
        n = float(value)
    except (ValueError, TypeError, OverflowError):
        raise ResearchRejected(name + ": nonnumeric") from None
    if not isfinite(n) or (positive and n <= 0) or (nonnegative and n < 0):
        raise ResearchRejected(name + ": invalid range")
    return n

def validate_walk_forward(samples):
    if not isinstance(samples, list) or not samples:
        raise ResearchRejected("missing walk-forward samples")
    results = []
    last_end = None
    for s in samples:
        if not isinstance(s, dict):
            raise ResearchRejected("invalid sample")
        try:
            train_start, train_end, test_start, test_end = (datetime.fromisoformat(s[k]) for k in ("train_start","train_end","test_start","test_end"))
        except (KeyError, ValueError, TypeError):
            raise ResearchRejected("missing/invalid chronological evidence") from None
        if not (train_start < train_end < test_start < test_end) or (last_end is not None and test_start <= last_end):
            raise ResearchRejected("overlapping or unordered periods")
        last_end = test_end
        train_pf = finite_number(s.get("train_profit_factor"),"train_pf",positive=True)
        test_pf = finite_number(s.get("test_profit_factor"),"test_pf",nonnegative=True)
        test_payoff = finite_number(s.get("test_payoff"),"test_payoff",nonnegative=True)
        trades = finite_number(s.get("test_trades"),"test_trades",nonnegative=True)
        dd = finite_number(s.get("test_max_drawdown"),"drawdown",nonnegative=True)
        if not trades.is_integer():
            raise ResearchRejected("noninteger trade count")
        degradation = max(0.0,(train_pf-test_pf)/train_pf)
        passed = trades >= 30 and test_pf >= 1.5 and test_payoff >= 3 and dd <= 10 and degradation <= .35
        results.append({"passed":passed,"degradation":degradation,"promotion_allowed":False})
    return {"all_passed":all(x["passed"] for x in results),"samples":results,"promotion_allowed":False,"mode":"PAPER_ONLY"}

def anti_overfit_validate(edge):
    if not isinstance(edge,dict):
        raise ResearchRejected("missing edge")
    fields = ("symbols_tested","years_tested","regimes_tested","out_of_sample_profit_factor","out_of_sample_payoff","out_of_sample_expectancy","max_drawdown","parameter_sensitivity")
    vals = {k:finite_number(edge.get(k),k,nonnegative=(k!="out_of_sample_expectancy")) for k in fields}
    if any(not vals[k].is_integer() for k in ("symbols_tested","years_tested","regimes_tested")):
        raise ResearchRejected("invalid diversity count")
    passed = (vals["symbols_tested"]>=3 and vals["years_tested"]>=3 and vals["regimes_tested"]>=3 and vals["out_of_sample_profit_factor"]>=1.5 and vals["out_of_sample_payoff"]>=3 and vals["out_of_sample_expectancy"]>0 and vals["max_drawdown"]<=10 and vals["parameter_sensitivity"]<=35)
    return {"passed":passed,"decision":"RESEARCH_PASS_ONLY" if passed else "REJECT","promotion_allowed":False,"mode":"PAPER_ONLY"}

def portfolio_exposure(trades, *, max_abs_lots=0.03):
    threshold=finite_number(max_abs_lots,"max_abs_lots",positive=True)
    if not isinstance(trades,list):
        raise ResearchRejected("invalid trades")
    exposure={}
    for t in trades:
        if not isinstance(t,dict):
            raise ResearchRejected("invalid trade")
        symbol=t.get("symbol")
        side=t.get("side")
        if symbol not in FX_BASE or side not in ("BUY","SELL"):
            raise ResearchRejected("unsupported symbol/side")
        lot=finite_number(t.get("lot"),"lot",positive=True)
        base,quote=FX_BASE[symbol]
        direction=1 if side=="BUY" else -1
        exposure[base]=exposure.get(base,0.0)+direction*lot
        exposure[quote]=exposure.get(quote,0.0)-direction*lot
    concentration=max((abs(x) for x in exposure.values()),default=0)
    return {"exposure_lot_proxy":exposure,"max_abs_lots":concentration,"approved":concentration < threshold,"promotion_allowed":False,"mode":"PAPER_ONLY","note":"lot proxy only; not notional or true correlation"}

def correlation_precheck(existing,new_trade, *, max_abs_lots=0.03):
    before=portfolio_exposure(existing,max_abs_lots=max_abs_lots)
    after=portfolio_exposure(existing+[new_trade],max_abs_lots=max_abs_lots)
    return {"approved":after["approved"],"before":before,"after":after,"promotion_allowed":False}

def safety_contract():
    return {"mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","broker_execution":"DISABLED","promotion_allowed":False,"operational_certified":False}
