"""P2614 chronological PAPER replay adapter; no broker connectivity."""
import heapq
import math

def replay_chronological(edges, candles, features, simulate_fill, *, initial_capital=100.0, risk_pct=0.01, max_trades_per_day=20, warmup=60, tail=20):
    if not math.isfinite(initial_capital) or initial_capital <= 0: raise ValueError("invalid capital")
    if not math.isfinite(risk_pct) or not 0 < risk_pct <= 1: raise ValueError("invalid risk")
    if type(max_trades_per_day) is not int or max_trades_per_day < 1: raise ValueError("invalid daily limit")
    if any(e.get("direction") not in ("BUY_PAPER", "SELL_PAPER") for e in edges): raise ValueError("non PAPER direction")
    if len({e["edge_id"] for e in edges}) != len(edges): raise ValueError("duplicate edge id")
    capital = peak = float(initial_capital)
    pending, busy, trades, curve, daily = [], set(), [], [], {}
    seq = 0
    def settle(bar):
        nonlocal capital, peak
        while pending and pending[0][0] <= bar:
            _, _, fill = heapq.heappop(pending)
            pnl = fill["risk_usd"] * fill["r"]
            capital = max(0.01, capital + pnl)
            peak = max(peak, capital)
            fill.update(capital_after=round(capital, 6), pnl_usd=round(pnl, 6),
                        dd_pct=round((peak-capital)/peak*100, 6))
            trades.append(fill)
            busy.remove(fill["edge_id"])
    for i in range(warmup, max(warmup, len(candles)-tail)):
        settle(i)
        day = candles[i]["time"].date().isoformat()
        daily.setdefault(day, 0)
        for edge in edges:
            if daily[day] >= max_trades_per_day: break
            eid = edge["edge_id"]
            if eid in busy: continue
            fill = simulate_fill(edge, candles, features, i)
            if fill is None: continue
            if fill.get("real_execution_allowed") is not False: raise ValueError("real execution flag")
            entry, exit_ = fill["entry_i"], fill["exit_i"]
            if type(entry) is not int or type(exit_) is not int or not i < entry < exit_ < len(candles):
                raise ValueError("invalid fill chronology")
            r = float(fill["r"])
            if not math.isfinite(r): raise ValueError("invalid R")
            fill = dict(fill, edge_id=eid, risk_usd=capital*risk_pct,
                        capital_before=round(capital, 6))
            heapq.heappush(pending, (exit_, seq, fill))
            seq += 1
            busy.add(eid)
            daily[day] += 1
        curve.append({"bar": i, "capital": round(capital, 6),
                      "dd_pct": round((peak-capital)/peak*100, 6)})
    settle(len(candles))
    return {"initial_capital_usd": initial_capital, "final_capital_usd": round(capital, 6),
            "trades": len(trades), "max_dd_pct": max([x["dd_pct"] for x in trades], default=0),
            "real_execution_allowed": False}, curve, trades
