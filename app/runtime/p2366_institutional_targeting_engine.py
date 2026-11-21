from __future__ import annotations

def institutional_targets(ctx: dict) -> dict:
    def number(key, fallback):
        value = ctx.get(key)
        return float(fallback if value is None else value)

    entry=number("entry", 0)
    stop=float(ctx["stop"])
    side=str(ctx["side"]).upper()
    swing_high=number("swing_high", entry)
    swing_low=number("swing_low", entry)
    atr=number("atr", 0)
    session_high=number("session_high", swing_high)
    session_low=number("session_low", swing_low)
    liquidity_high=number("liquidity_high", session_high)
    liquidity_low=number("liquidity_low", session_low)
    vwap=number("vwap", entry)
    round_number=number("round_number", entry)

    risk=abs(entry-stop)
    if side not in ("BUY", "SELL") or risk<=0:
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
        candidates=[x for x in candidates if x>entry]
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
        candidates=[x for x in candidates if x<entry]
        target=min(candidates) if candidates else entry
        rr=(entry-target)/risk
        partial_1=entry-risk
        partial_2=entry-risk*2

    rr=round(rr,2)

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
