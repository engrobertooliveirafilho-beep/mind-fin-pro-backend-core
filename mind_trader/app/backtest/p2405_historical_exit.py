"""ET665 M10: causal OHLCV stop/target exit selector for offline PAPER replay.

Only bars strictly AFTER the historical entry fill timestamp are eligible.
Gap exits use the first tradable bar open; same-bar ambiguity favors stop.
"""
import math
from mind_trader.app.backtest.market_core import load_ohlcv


def select_historical_exit(symbol, timeframe, db_path, *, fill_ts, side, stop, target):
    if not isinstance(fill_ts, str) or not fill_ts or side not in ("BUY", "SELL"):
        raise ValueError("INVALID_EXIT_REQUEST")
    if not all(type(x) in (int,float) and math.isfinite(x) and x > 0 for x in (stop,target)):
        raise ValueError("INVALID_STOP_TARGET")
    if (side == "BUY" and stop >= target) or (side == "SELL" and stop <= target):
        raise ValueError("INVALID_STOP_TARGET_ORDER")
    rows = load_ohlcv(symbol,timeframe,db_path)
    times = [str(r["ts"]) for r in rows]
    if any(a >= b for a,b in zip(times,times[1:])):
        raise ValueError("NON_MONOTONIC_HISTORY")
    if times.count(fill_ts) != 1:
        raise ValueError("ENTRY_BAR_NOT_FOUND")
    start = times.index(fill_ts) + 1
    for row in rows[start:]:
        op, hi, lo, close = (row[k] for k in ("open","high","low","close"))
        if any(type(x) not in (int,float) or not math.isfinite(x) or x <= 0 for x in (op,hi,lo,close)):
            raise ValueError("INVALID_EXIT_BAR")
        if lo > min(op,close) or hi < max(op,close):
            raise ValueError("INVALID_EXIT_CANDLE")
        if side == "BUY":
            if op <= stop:
                price, reason = op, "STOP_GAP"
            elif op >= target:
                price, reason = op, "TARGET_GAP"
            elif lo <= stop:
                price, reason = stop, "STOP"
            elif hi >= target:
                price, reason = target, "TARGET"
            else:
                continue
        else:
            if op >= stop:
                price, reason = op, "STOP_GAP"
            elif op <= target:
                price, reason = op, "TARGET_GAP"
            elif hi >= stop:
                price, reason = stop, "STOP"
            elif lo <= target:
                price, reason = target, "TARGET"
            else:
                continue
        return {"decision":"M10_HISTORICAL_EXIT_SELECTED","exit_ts":str(row["ts"]),
                "exit_close":float(price),"exit_reason":reason,"production":"BLOCKED",
                "real_broker_routing":"DISABLED"}
    return {"decision":"BLOCK_NO_HISTORICAL_EXIT","production":"BLOCKED",
            "real_broker_routing":"DISABLED"}
