import math


def _finite_number(value):
    if isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False


def simulate_fill(order, spread=0.0, slippage=0.0, commission=0.0):
    if not isinstance(order, dict):
        return {"filled": False, "decision": "FILL_REJECT_INVALID_ORDER"}

    entry_raw = order.get("entry")
    stop_raw = order.get("stop")
    target_raw = order.get("target")
    side_raw = order.get("side", "BUY")

    if not all(_finite_number(x) for x in (entry_raw, stop_raw, target_raw)):
        return {"filled": False, "decision": "FILL_REJECT_INVALID_PRICE"}
    if not all(_finite_number(x) for x in (spread, slippage, commission)):
        return {"filled": False, "decision": "FILL_REJECT_INVALID_COST"}
    if any(float(x) < 0 for x in (spread, slippage, commission)):
        return {"filled": False, "decision": "FILL_REJECT_NEGATIVE_COST"}

    entry, stop, target = float(entry_raw), float(stop_raw), float(target_raw)
    spread, slippage, commission = float(spread), float(slippage), float(commission)
    if entry <= 0 or stop <= 0 or target <= 0:
        return {"filled": False, "decision": "FILL_REJECT_INVALID_PRICE"}

    if not isinstance(side_raw, str):
        return {"filled": False, "decision": "FILL_REJECT_INVALID_SIDE"}
    side = side_raw.upper()
    if side == "BUY":
        if not stop < entry < target:
            return {"filled": False, "decision": "FILL_REJECT_INVALID_BUY_BRACKETS"}
        fill_price = entry + spread / 2 + slippage
    elif side == "SELL":
        if not target < entry < stop:
            return {"filled": False, "decision": "FILL_REJECT_INVALID_SELL_BRACKETS"}
        fill_price = entry - spread / 2 - slippage
        if fill_price <= 0:
            return {"filled": False, "decision": "FILL_REJECT_NONPOSITIVE_FILL"}
    else:
        return {"filled": False, "decision": "FILL_REJECT_INVALID_SIDE"}

    return {
        "filled": True,
        "decision": "FILL_SIMULATED",
        "side": side,
        "requested_entry": entry,
        "stop": stop,
        "target": target,
        "fill_price": fill_price,
        "spread": spread,
        "slippage": slippage,
        "commission": commission,
        "production": "BLOCKED",
        "live": "FORBIDDEN",
        "edge_claim": "NONE",
    }
