"""ET665.R375: bind trade-derived walk-forward metrics to measured correlation.

All strategies share aligned PAPER R-multiple observations for correlation.
Research-only: no historical fills, promotion, broker or Phase B certification.
"""
from mind_trader.experimental.et665_r373_trade_metric_adapter import evaluate_trades
from mind_trader.experimental.et665_r374_correlation_gate import assess

def evaluate_portfolio(windows_by_strategy,max_abs_correlation="0.8"):
    if not isinstance(windows_by_strategy,dict) or len(windows_by_strategy)<2:
        raise ValueError("at least two strategies required")
    results={};series={}
    for name,windows in sorted(windows_by_strategy.items()):
        if not isinstance(name,str) or not name:
            raise ValueError("invalid strategy name")
        if not isinstance(windows,list) or len(windows)!=5:
            raise ValueError("exactly five windows required")
        flattened=[]
        for w in windows:
            if not isinstance(w,dict) or set(w)!={"window_id","trades"} or not isinstance(w["trades"],list):
                raise ValueError("invalid window")
            flattened.extend(w["trades"])
        series[name]=flattened
        # Correlation cannot be self-attested; use measured result below.
        results[name]=evaluate_trades(windows,True)
    identities=[tuple((w["window_id"],len(w["trades"])) for w in windows) for windows in windows_by_strategy.values()]
    if any(x!=identities[0] for x in identities[1:]):
        raise ValueError("misaligned windows")
    corr=assess(series,max_abs_correlation)
    passed=corr["status"]=="PASS" and all(r["research_gate"]=="PASS" for r in results.values())
    return {"status":"RESEARCH_GATE_PASS" if passed else "BLOCKED",
            "strategy_results":results,"measured_correlation":corr,
            "correlation_source":"MEASURED_NOT_SELF_ATTESTED",
            "historical_fills_verified":False,"official_p2405f_certified":False,
            "phase_b_certified":False,"strategy_promotion_authorized":False,
            "real_orders":"FORBIDDEN"}
