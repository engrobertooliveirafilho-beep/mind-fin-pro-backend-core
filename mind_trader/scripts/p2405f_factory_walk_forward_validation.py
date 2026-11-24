"""Quarantine historical hash-derived P2405F metrics."""
def eval_cand(candidate):
    return {**candidate, "decision":"BLOCKED_SYNTHETIC_METRICS",
            "core_pass":False,"ideal_dd_pass":False,"max_dd_pass":False,
            "real_execution_allowed":False,"runtime_promotion_allowed":False,
            "mode":"PAPER_ONLY","real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
            **dict.fromkeys(("pf","winrate","expectancy","max_dd_r","samples","windows","passed_windows"),None)}
