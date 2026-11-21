"""ET665: independently recompute offline walk-forward metrics from closed trades.

Research-only gate: never authorizes runtime or real orders.
"""
import math

def evaluate_walk_forward(trades, windows, *, min_samples=30, min_passed=4, min_window_samples=6):
    if any(type(v) is not int or v < 1 for v in (min_samples, min_passed, min_window_samples)) or min_passed > 5:
        raise ValueError("invalid evaluation thresholds")
    if not isinstance(trades, (list, tuple)) or not isinstance(windows, (list, tuple)) or len(windows) != 5:
        raise ValueError("five independent chronological windows required")
    if len(trades) < min_samples:
        raise ValueError("insufficient verified trades")
    if any(type(w) is not dict or type(w.get("start")) is not int or type(w.get("end")) is not int or w["start"] >= w["end"] for w in windows):
        raise ValueError("invalid window boundaries")
    if any(windows[j]["end"] > windows[j+1]["start"] for j in range(4)):
        raise ValueError("overlapping windows")
    if any(type(t) is not dict or type(t.get("exit_i")) is not int or type(t.get("entry_i")) is not int or t["entry_i"] >= t["exit_i"] or type(t.get("r")) not in (int,float) or not math.isfinite(t["r"]) or t.get("real_execution_allowed") is not False for t in trades):
        raise ValueError("invalid or non PAPER trade")
    if any(trades[j]["exit_i"] > trades[j+1]["exit_i"] for j in range(len(trades)-1)):
        raise ValueError("trades not ordered by exit")
    assigned = [[] for _ in windows]
    for t in trades:
        matches = [k for k,w in enumerate(windows) if w["start"] <= t["entry_i"] < t["exit_i"] <= w["end"]]
        if len(matches) != 1: raise ValueError("unassigned or boundary-crossing trade")
        assigned[matches[0]].append(t["r"])
    if any(not x for x in assigned): raise ValueError("empty validation window")
    def metrics(rs):
        gain = sum(x for x in rs if x > 0)
        loss = -sum(x for x in rs if x < 0)
        pf = gain/loss if loss else math.inf
        wr = 100*sum(x>0 for x in rs)/len(rs)
        exp = sum(rs)/len(rs)
        eq = peak = dd = 0.
        for r in rs:
            eq += r
            peak = max(peak,eq)
            dd = max(dd,peak-eq)
        return {"pf":pf,"winrate":wr,"expectancy":exp,"max_dd_r":dd,"samples":len(rs)}
    wm = [metrics(x) for x in assigned]
    passed = sum(m["pf"] >= 1.5 and m["winrate"] >= 45 and m["expectancy"] > 0 and m["samples"] >= min_window_samples for m in wm)
    total = metrics([t["r"] for t in trades])
    qualifies = (passed >= min_passed and total["pf"] >= 1.5 and total["winrate"] >= 45 and total["expectancy"] > 0 and total["max_dd_r"] <= 12)
    return {"research_qualified":qualifies,"runtime_allowed":False,"real_execution_allowed":False,
            "passed_windows":passed,"windows":wm,"overall":total,"min_window_samples":min_window_samples,
            "source":"RECOMPUTED_FROM_SUPPLIED_TRADES_NOT_INDEPENDENTLY_AUTHENTICATED"}
