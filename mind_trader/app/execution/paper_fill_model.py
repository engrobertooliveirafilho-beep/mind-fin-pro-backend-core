import math

def simulate_fill(order, spread=0.0, slippage=0.0, commission=0.0):
    if not isinstance(order, dict):
        return {"filled":False,"decision":"FILL_REJECT_INVALID_PRICE"}
    values=[order.get(k) for k in ("entry","stop","target")]
    try:
        valid=all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in values)
        costs=all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in (spread,slippage,commission))
    except (OverflowError,TypeError,ValueError):
        valid=costs=False
    if not valid or not costs:
        return {"filled":False,"decision":"FILL_REJECT_INVALID_PRICE_OR_COST"}
    entry=float(order["entry"])
    stop=order.get("stop")
    target=order.get("target")
    side=order.get("side")

    if entry <= 0 or stop is None or target is None:
        return {"filled":False,"decision":"FILL_REJECT_INVALID_PRICE"}

    if side=="BUY":
        fill_price=entry + spread/2 + slippage
    elif side=="SELL":
        fill_price=entry - spread/2 - slippage
    else:
        return {"filled":False,"decision":"FILL_REJECT_INVALID_SIDE"}

    if not math.isfinite(fill_price) or fill_price<=0 or not (stop<entry<target and stop<fill_price<target if side=="BUY" else target<entry<stop and target<fill_price<stop):
        return {"filled":False,"decision":"FILL_REJECT_PRICE_GEOMETRY"}

    return {
        "filled":True,
        "decision":"FILL_SIMULATED",
        "side":side,
        "requested_entry":entry,
        "fill_price":fill_price,
        "spread":spread,
        "slippage":slippage,
        "commission":commission,
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
