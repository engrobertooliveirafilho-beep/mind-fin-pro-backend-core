from __future__ import annotations
from math import isfinite

def institutional_targets(ctx: dict) -> dict:
    blocked = {"approved":False,"decision":"BLOCK_INVALID_RISK","mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN"}
    if ctx.get("side") not in ("BUY", "SELL"):
        return blocked
    for key in ("entry","stop","swing_high","swing_low","atr","session_high","session_low","liquidity_high","liquidity_low","vwap","round_number"):
        if key not in ctx and key not in ("entry","stop"):
            continue
        v = ctx.get(key)
        if type(v) not in (int,float) or not isfinite(v) or v < 0 or (key != "atr" and v == 0):
            return blocked
    if (ctx["side"] == "BUY" and ctx["stop"] >= ctx["entry"]) or (ctx["side"] == "SELL" and ctx["stop"] <= ctx["entry"]):
        return blocked
    entry=float(ctx["entry"])
    stop=float(ctx["stop"])
    side=str(ctx["side"]).upper()
    swing_high=float(ctx.get("swing_high", entry))
    swing_low=float(ctx.get("swing_low", entry))
    atr=float(ctx.get("atr", 0))
    session_high=float(ctx.get("session_high", swing_high))
    session_low=float(ctx.get("session_low", swing_low))
    liquidity_high=float(ctx.get("liquidity_high", session_high))
    liquidity_low=float(ctx.get("liquidity_low", session_low))
    vwap=float(ctx.get("vwap", entry))
    round_number=float(ctx.get("round_number", entry))

    risk=abs(entry-stop)
    if risk<=0:
        return {"approved":False,"decision":"BLOCK_INVALID_RISK","mode":"PAPER_ONLY","real_orders":"FORBIDDEN"}

    move=abs(swing_high-swing_low)

    if side=="BUY":
        candidates=[
            entry + move*1.618,
            entry + move*2.618,
            session_high,
            liquidity_high,
            vwap + atr*2,
            entry + atr*2,
            round_number
        ]
        candidates=[x for x in candidates if x>entry and isfinite(x)]
        target=max(candidates) if candidates else entry
        rr=(target-entry)/risk
        partial_1=entry+risk
        partial_2=entry+risk*2
    else:
        candidates=[
            entry - move*1.618,
            entry - move*2.618,
            session_low,
            liquidity_low,
            vwap - atr*2,
            entry - atr*2,
            round_number
        ]
        candidates=[x for x in candidates if 0<x<entry and isfinite(x)]
        target=min(candidates) if candidates else entry
        rr=(entry-target)/risk
        partial_1=entry-risk
        partial_2=entry-risk*2

    if not isfinite(rr):
        return blocked

    if rr < 2:
        decision="BLOCK_TARGET_BELOW_2R"
    elif rr < 3:
        decision="APPROVED_STANDARD"
    elif rr < 5:
        decision="APPROVED_PRIORITY"
    else:
        decision="APPROVED_INSTITUTIONAL"

    return {
        "side":side,
        "entry":entry,
        "stop":stop,
        "risk":round(risk,4),
        "target":round(target,4),
        "rr":rr,
        "partial_1R":round(partial_1,4),
        "partial_2R":round(partial_2,4),
        "approved":rr>=2,
        "decision":decision,
        "target_sources":"FIBO|LIQUIDITY|SESSION_HIGH_LOW|VWAP|ATR|ROUND_NUMBER",
        "target_min_rr":2.0,
        "target_priority_rr":3.0,
        "target_institutional_rr":5.0,
        "mode":"PAPER_ONLY",
        "real_orders":"FORBIDDEN",
        "ftmo_real":"FORBIDDEN"
    }

def health() -> dict:
    return {
        "status":"OK",
        "engine":"P2366_INSTITUTIONAL_TARGETING_ENGINE",
        "target_min_rr":2.0,
        "mode":"PAPER_ONLY",
        "real_orders":"FORBIDDEN",
        "ftmo_real":"FORBIDDEN"
    }
