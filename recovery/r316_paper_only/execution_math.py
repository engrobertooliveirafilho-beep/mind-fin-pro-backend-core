"""PAPER_ONLY execution arithmetic. No broker connectivity or order submission."""
from math import isfinite

def resolve_exit(side: str, high: float, low: float, stop: float, target: float):
    """Conservative stop-first policy for ambiguous OHLC candles."""
    if side not in ('BUY', 'SELL'):
        raise ValueError('invalid side')
    if not all(isfinite(float(x)) for x in (high, low, stop, target)) or low > high:
        raise ValueError('invalid prices')
    if side == 'BUY':
        if stop >= target: raise ValueError('invalid BUY levels')
        return ('stop', stop) if low <= stop else (('target', target) if high >= target else (None, None))
    if target >= stop: raise ValueError('invalid SELL levels')
    return ('stop', stop) if high >= stop else (('target', target) if low <= target else (None, None))

def execution_price(price: float, action: str, fees_bps: float):
    """Apply adverse execution friction per BUY or SELL leg; not a fee accounting ledger."""
    if action not in ('BUY','SELL') or not isfinite(float(price)) or price <= 0 or not isfinite(float(fees_bps)) or fees_bps < 0 or fees_bps >= 10000:
        raise ValueError('invalid execution inputs')
    return float(price) * (1 + fees_bps / 10000 if action == 'BUY' else 1 - fees_bps / 10000)

def trade_r(side, entry, stop, exit_price, fees_bps=0):
    if side not in ('BUY','SELL') or entry <= 0 or stop <= 0 or exit_price <= 0:
        raise ValueError('invalid trade')
    if (side == 'BUY' and stop >= entry) or (side == 'SELL' and stop <= entry):
        raise ValueError('invalid risk geometry')
    buy = side == 'BUY'
    fill_entry = execution_price(entry, 'BUY' if buy else 'SELL', fees_bps)
    fill_exit = execution_price(exit_price, 'SELL' if buy else 'BUY', fees_bps)
    risk = abs(entry-stop)
    return (fill_exit-fill_entry if buy else fill_entry-fill_exit) / risk
