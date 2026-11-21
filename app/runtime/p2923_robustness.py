# P2923 offline research engine; execution and promotion are permanently disabled.
"""P2923 robustness engine. Offline research only; never promotes or executes."""
import math
import random

MODE = "BACKTEST_PAPER_ONLY"
EXECUTION_ALLOWED = False
CAPITAL_ALLOCATION = 0.0
PROMOTION_ALLOWED = False

def _finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError, OverflowError):
        return False

def _percentile(values, p):
    ordered = sorted(values)
    index = min(max(int(math.ceil((len(ordered) - 1) * p)), 0), len(ordered) - 1)
    return ordered[index]

def block_bootstrap(trade_r, runs=1000, initial_capital=100.0,
                    risk_fraction=0.0025, block_size=5, seed=2923):
    if not isinstance(trade_r, (list, tuple)) or not trade_r:
        raise ValueError("MISSING_TRADE_RETURN_SERIES")
    if any(not _finite(x) for x in trade_r):
        raise ValueError("INVALID_TRADE_RETURN")
    if isinstance(runs, bool) or not isinstance(runs, int) or runs < 1:
        raise ValueError("INVALID_RUN_COUNT")
    if not _finite(initial_capital) or initial_capital <= 0:
        raise ValueError("INVALID_INITIAL_CAPITAL")
    if not _finite(risk_fraction) or not 0 < risk_fraction <= 1:
        raise ValueError("INVALID_RISK_FRACTION")
    if isinstance(block_size, bool) or not isinstance(block_size, int) or not 1 <= block_size <= len(trade_r):
        raise ValueError("INVALID_BLOCK_SIZE")

    rs = [float(x) for x in trade_r]
    n = len(rs)
    finals, drawdowns = [], []
    for run in range(runs):
        rng = random.Random(seed + run)
        sample = []
        while len(sample) < n:
            start = rng.randrange(n)
            sample.extend(rs[(start + offset) % n] for offset in range(block_size))
        sample = sample[:n]

        equity = float(initial_capital)
        peak = equity
        max_dd = 0.0
        for r_value in sample:
            equity = max(0.01, equity * (1.0 + risk_fraction * r_value))
            if not math.isfinite(equity):
                raise ValueError("NONFINITE_EQUITY")
            peak = max(peak, equity)
            max_dd = max(max_dd, (peak - equity) / peak * 100.0)
        finals.append(equity)
        drawdowns.append(max_dd)

    return {
        "method": "CIRCULAR_BLOCK_BOOTSTRAP",
        "runs": runs,
        "block_size": block_size,
        "sample_count": n,
        "p05_final": round(_percentile(finals, 0.05), 6),
        "p50_final": round(_percentile(finals, 0.50), 6),
        "p95_final": round(_percentile(finals, 0.95), 6),
        "p50_max_dd_pct": round(_percentile(drawdowns, 0.50), 6),
        "p95_max_dd_pct": round(_percentile(drawdowns, 0.95), 6),
        "probability_positive": round(sum(x > initial_capital for x in finals) / runs, 6),
    }

def regime_metrics(trades):
    if not isinstance(trades, (list, tuple)) or not trades:
        raise ValueError("MISSING_REGIME_TRADE_SERIES")
    groups = {}
    for index, trade in enumerate(trades):
        if not isinstance(trade, dict) or not _finite(trade.get("r")):
            raise ValueError(f"INVALID_REGIME_TRADE:{index}")
        regime = trade.get("regime")
        if not isinstance(regime, str) or not regime.strip():
            raise ValueError(f"MISSING_REGIME_LABEL:{index}")
        groups.setdefault(regime, []).append(float(trade["r"]))

    result = {}
    for regime, values in sorted(groups.items()):
        wins = [x for x in values if x > 0]
        losses = [x for x in values if x < 0]
        gross_loss = abs(sum(losses))
        equity = peak = max_dd = 0.0
        for value in values:
            equity += value
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)
        result[regime] = {
            "samples": len(values),
            "wins": len(wins),
            "losses": len(losses),
            "expectancy_r": round(sum(values) / len(values), 8),
            "profit_factor": round(sum(wins) / gross_loss, 8) if gross_loss else None,
            "max_drawdown_r": round(max_dd, 8),
        }
    return result

def evaluate_candidate(candidate, trades, min_samples_per_partition=30,
                       runs=1000, risk_fraction=0.0025, block_size=5):
    base = {
        "execution_allowed": False,
        "capital_allocation": 0.0,
        "promotion_allowed": False,
        "mode": MODE,
    }
    if not isinstance(candidate, dict):
        return {**base, "status": "BLOCKED_INVALID_CANDIDATE"}
    if candidate.get("walk_forward_status") != "WALK_FORWARD_PASS":
        return {**base, "status": "BLOCKED_WALK_FORWARD_NOT_PASSED"}

    sample_fields = ("samples_train", "samples_validation", "samples_test")
    samples = {}
    for field in sample_fields:
        value = candidate.get(field)
        if type(value) is not int or value < 0:
            return {**base, "status": "BLOCKED_INVALID_SAMPLE_COUNTS", "field": field}
        samples[field] = value
    if isinstance(min_samples_per_partition, bool) or not isinstance(min_samples_per_partition, int) or min_samples_per_partition < 1:
        return {**base, "status": "BLOCKED_INVALID_SAMPLE_POLICY"}
    insufficient = {key: value for key, value in samples.items() if value < min_samples_per_partition}
    if insufficient:
        return {**base, "status": "BLOCKED_LOW_SAMPLE_SIZE", "sample_counts": samples,
                "minimum_per_partition": min_samples_per_partition, "insufficient_partitions": insufficient}

    if not isinstance(trades, (list, tuple)) or not trades:
        return {**base, "status": "BLOCKED_MISSING_RAW_TRADE_SERIES", "sample_counts": samples}
    if len(trades) < min_samples_per_partition:
        return {**base, "status": "BLOCKED_RAW_SERIES_TOO_SHORT", "raw_trade_count": len(trades)}

    try:
        regimes = regime_metrics(trades)
        monte_carlo = block_bootstrap(
            [trade["r"] for trade in trades],
            runs=runs,
            risk_fraction=risk_fraction,
            block_size=block_size,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return {**base, "status": "BLOCKED_INVALID_ROBUSTNESS_INPUT", "reason": str(exc)}

    if len(regimes) < 2:
        return {**base, "status": "BLOCKED_INSUFFICIENT_REGIME_COVERAGE",
                "regimes": regimes, "monte_carlo": monte_carlo}
    return {**base, "status": "ROBUSTNESS_REVIEW_REQUIRED",
            "sample_counts": samples, "regimes": regimes, "monte_carlo": monte_carlo}

def safety_contract():
    return {
        "mode": MODE,
        "execution_allowed": False,
        "capital_allocation": 0.0,
        "promotion_allowed": False,
        "purpose": "offline_block_bootstrap_and_regime_robustness",
    }
