"""ET665.R301: source-authority gate for historical P2403 replay artifacts.
Historical P2403C invalidates P2403B's claimed correlation readiness.
No broker/network access, promotion, or execution.
"""
from pathlib import Path

INVALID_SOURCE_BASENAMES = frozenset({
    "de40_cycle_events.csv",
    "p2403b_edge_trade_series.csv",
    "p2403e_de40_edge_trade_series.csv",
})

def check_replay_source(source_path, *, source_kind, causal_signal_verified=False,
                        independent_ohlc_verified=False):
    name = Path(source_path).name.lower() if isinstance(source_path, (str, Path)) else ""
    issues = []
    if not name:
        issues.append("SOURCE_MISSING")
    if name in INVALID_SOURCE_BASENAMES:
        issues.append("HISTORICAL_SOURCE_QUARANTINED")
    if source_kind != "CAUSAL_STRATEGY_REPLAY":
        issues.append("SOURCE_KIND_UNVERIFIED")
    if causal_signal_verified is not True:
        issues.append("CAUSAL_SIGNAL_NOT_VERIFIED")
    if independent_ohlc_verified is not True:
        issues.append("OHLC_NOT_INDEPENDENTLY_VERIFIED")
    # Passing this narrow preflight still cannot certify a strategy or permit runtime.
    return {
        "source_preflight_pass": not issues,
        "issues": issues,
        "temporal_correlation_certified": False,
        "strategy_certified": False,
        "runtime_promotion_allowed": False,
        "status": "QUARANTINE",
    }
