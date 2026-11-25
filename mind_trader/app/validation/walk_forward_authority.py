import json, math, statistics
from pathlib import Path
from datetime import datetime, UTC


def walk_forward_authority(windows):
    if not isinstance(windows, (list, tuple)) or len(windows) < 3:
        return {"decision":"WALK_FORWARD_INSUFFICIENT_WINDOWS","passed":False,"production":"BLOCKED","edge_claim":"NONE"}

    expectancies = []
    pfs = []
    for window in windows:
        if not isinstance(window, dict) or "expectancy" not in window or "profit_factor" not in window:
            return {"decision":"WALK_FORWARD_INVALID_WINDOW_DATA","passed":False,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"}
        try:
            expectancy = float(window["expectancy"])
            profit_factor = float(window["profit_factor"])
        except (TypeError, ValueError, OverflowError):
            return {"decision":"WALK_FORWARD_INVALID_WINDOW_DATA","passed":False,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"}
        # P2279E/P8 backtests encode an undefined PF (no gross losses) as 999.
        # It is not a finite robustness result and must never count as a pass.
        if not math.isfinite(expectancy) or not math.isfinite(profit_factor) or profit_factor <= 0 or profit_factor >= 999:
            return {"decision":"WALK_FORWARD_INVALID_WINDOW_DATA","passed":False,"production":"BLOCKED","live":"FORBIDDEN","edge_claim":"NONE"}
        expectancies.append(expectancy)
        pfs.append(profit_factor)

    positive = sum(1 for value in expectancies if value > 0)
    avg_exp = statistics.mean(expectancies)
    min_pf = min(pfs)
    consistency = positive / len(windows)
    passed = avg_exp > 0 and min_pf > 1.05 and consistency >= 0.67
    return {
        "authority":"P8.81_WALK_FORWARD_AUTHORITY",
        "windows":len(windows),
        "avg_expectancy":avg_exp,
        "min_profit_factor":min_pf,
        "positive_window_ratio":consistency,
        "passed":passed,
        "decision":"WALK_FORWARD_PASS_RESEARCH_ONLY" if passed else "WALK_FORWARD_REJECT_OR_RETEST",
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }


def save_walk_forward_authority(report,path="mind_trader/reports/P8.81_walk_forward_authority.json"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
