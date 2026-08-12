def simulate_fill(order, spread=0.0, slippage=0.0, commission=0.0):
    entry=float(order.get("entry",0))
    stop=order.get("stop")
    target=order.get("target")
    side=order.get("side","BUY").upper()

    if entry <= 0 or stop is None or target is None:
        return {"filled":False,"decision":"FILL_REJECT_INVALID_PRICE"}

    if side=="BUY":
        fill_price=entry + spread/2 + slippage
    elif side=="SELL":
        fill_price=entry - spread/2 - slippage
    else:
        return {"filled":False,"decision":"FILL_REJECT_INVALID_SIDE"}

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
