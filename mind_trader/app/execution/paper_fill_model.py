"""Deterministic PAPER-only fill simulation. No broker or network operations."""
import math


def simulate_fill(order, spread=0.0, slippage=0.0, commission=0.0):
    rejected = {"filled": False, "decision": "FILL_REJECT_INVALID_PRICE"}
    if not isinstance(order, dict):
        return rejected
    side = order.get("side")
    if not isinstance(side, str) or side not in ("BUY", "SELL"):
        return {"filled": False, "decision": "FILL_REJECT_INVALID_SIDE"}
    values = (order.get("entry"), order.get("stop"), order.get("target"), spread, slippage, commission)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        return rejected
    entry, stop, target = values[:3]
    if entry <= 0 or stop <= 0 or target <= 0 or spread < 0 or slippage < 0 or commission < 0:
        return rejected
    if side == "BUY":
        fill_price = entry + spread / 2 + slippage
    else:
        fill_price = entry - spread / 2 - slippage
    if not math.isfinite(fill_price) or fill_price <= 0:
        return rejected
    return {
        "filled": True,
        "decision": "FILL_SIMULATED",
        "side": side,
        "requested_entry": entry,
        "fill_price": fill_price,
        "spread": spread,
        "slippage": slippage,
        "commission": commission,
        "production": "BLOCKED",
        "live": "FORBIDDEN",
        "edge_claim": "NONE",
    }
