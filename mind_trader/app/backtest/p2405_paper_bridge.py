"""ET665 M7: research-only chronological P2405 to PAPER signal bridge.

This module never places orders. Gateway submission requires a separate,
explicitly authorized caller and independent risk validation.
"""
import hashlib
import json
import math
from pathlib import Path

from mind_trader.app.backtest.market_core import load_ohlcv


def _finite_nonnegative(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError("INVALID_" + name)
    return float(value)


def prepare_paper_candidates(symbol, timeframe, db_path, *, fast=9, slow=21,
                             spread=0.0, slippage=0.0, commission=0.0,
                             checkpoint_path=None, telemetry_path=None):
    """Chronological SMA candidates, filled at NEXT bar open, never routed.

    Output is research telemetry, NOT a gateway-approved order. No future bars
    contribute to the signal at index i; fill occurs at index i+1.
    """
    if not isinstance(symbol, str) or not symbol.strip() or not isinstance(timeframe, str) or not timeframe.strip():
        raise ValueError("INVALID_INSTRUMENT")
    if type(fast) is not int or type(slow) is not int or fast < 2 or slow <= fast:
        raise ValueError("INVALID_SMA_WINDOWS")
    spread = _finite_nonnegative(spread, "SPREAD")
    slippage = _finite_nonnegative(slippage, "SLIPPAGE")
    commission = _finite_nonnegative(commission, "COMMISSION")
    rows = load_ohlcv(symbol, timeframe, db_path)
    if len(rows) < slow + 3:
        raise ValueError("INSUFFICIENT_CHRONOLOGICAL_DATA")
    times = [str(r["ts"]) for r in rows]
    if any(a >= b for a, b in zip(times, times[1:])):
        raise ValueError("NON_MONOTONIC_OR_DUPLICATE_TIMESTAMPS")
    for row in rows:
        for field in ("open", "high", "low", "close"):
            val = row[field]
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val) or val <= 0:
                raise ValueError("INVALID_OHLCV")
        if row["low"] > min(row["open"], row["close"]) or row["high"] < max(row["open"], row["close"]):
            raise ValueError("INVALID_CANDLE")
    closes = [float(r["close"]) for r in rows]
    def avg(end, n):
        return sum(closes[end - n + 1:end + 1]) / n
    events = []
    for i in range(slow, len(rows) - 1):
        prior_fast, prior_slow = avg(i - 1, fast), avg(i - 1, slow)
        current_fast, current_slow = avg(i, fast), avg(i, slow)
        direction = ("BUY" if prior_fast <= prior_slow and current_fast > current_slow
                     else "SELL" if prior_fast >= prior_slow and current_fast < current_slow
                     else None)
        if direction is None:
            continue
        next_open = float(rows[i + 1]["open"])
        friction = spread / 2 + slippage
        simulated_fill = next_open + friction if direction == "BUY" else next_open - friction
        event = {
            "symbol": symbol, "timeframe": timeframe, "strategy_id": "SMA_CROSS",
            "signal_ts": times[i], "fill_ts": times[i + 1],
            "side": direction, "simulated_fill": simulated_fill,
            "costs": {"spread": spread, "slippage": slippage, "commission": commission},
            "decision": "RESEARCH_ONLY_NOT_ROUTED", "real_orders": "FORBIDDEN",
        }
        event["candidate_id"] = hashlib.sha256(
            json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        events.append(event)
    result = {
        "decision": "PAPER_CANDIDATES_NOT_AUTHORIZED_FOR_ROUTING",
        "strategy": "SMA_CROSS", "bars": len(rows),
        "first_ts": times[0], "last_ts": times[-1],
        "events": events, "production": "BLOCKED", "real_orders": "FORBIDDEN",
        "checkpoint": {"last_processed_ts": times[-2], "last_candidate_id": events[-1]["candidate_id"] if events else None}
    }
    payload = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)
    for dest in (checkpoint_path, telemetry_path):
        if dest is not None:
            target = Path(dest)
            if target.exists():
                raise FileExistsError("EVIDENCE_IMMUTABLE:" + str(target))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(payload, encoding="utf-8")
    return result
