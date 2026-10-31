"""R342 causal DE40 validation gates. No live trading or promotion."""
from __future__ import annotations
import math

MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"

def causal_signal(current, previous):
    """Signal known at current candle close, never reads a future candle."""
    if previous is None:
        return None
    close = float(current["close"])
    prior = float(previous["close"])
    if not all(map(math.isfinite, (close, prior))) or close <= 0 or prior <= 0:
        raise ValueError("INVALID_PRICE")
    return 1 if close > prior else (-1 if close < prior else 0)

def score_next_candle(current, next_candle, direction):
    """Outcome is computed AFTER signal was frozen; no signal selection from outcome."""
    if direction not in (-1, 0, 1):
        raise ValueError("INVALID_DIRECTION")
    close = float(current["close"])
    future_close = float(next_candle["close"])
    high, low = float(current["high"]), float(current["low"])
    if not all(map(math.isfinite, (close, future_close, high, low))) or high <= low or close <= 0 or future_close <= 0:
        raise ValueError("INVALID_CANDLE")
    if direction == 0:
        return None
    return (future_close - close) * direction / (high - low)

def certification_report(*, success, source_sha_verified, oos_independent, ci_pass, no_lookahead, chronology_pass):
    gates = dict(success=bool(success), source_sha_verified=bool(source_sha_verified),
                 oos_independent=bool(oos_independent), ci_pass=bool(ci_pass),
                 no_lookahead=bool(no_lookahead), chronology_pass=bool(chronology_pass))
    certified = all(gates.values())
    return dict(status="CERTIFIED" if certified else "BLOCKED",
                certification="REPRODUCIBLE_OOS" if certified else "NOT_CERTIFIED",
                promotion_authorized=False, mode=MODE, real_orders=REAL_ORDERS,
                ftmo_real=FTMO_REAL, gates=gates)
