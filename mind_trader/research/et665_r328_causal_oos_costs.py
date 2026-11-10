"""ET665 R328 — cost-aware chronological OOS evaluation.

Research-only. This validates declared CSV structure and computes net-R
statistics in caller-defined chronological windows. It cannot independently
prove signal causality, source authority, or runtime eligibility.
"""
import math
from datetime import datetime, timedelta, timezone

from .et665_r315_immutable_csv_snapshot import snapshot_verified_csv

EXPECTED_COLUMNS = [
    "edge_id", "signal_id", "signal_timestamp", "entry_timestamp",
    "exit_timestamp", "pnl_gross_r", "spread_r", "slippage_r",
    "commission_r", "signal_logic_sha256", "market_data_sha256",
    "execution_record_sha256", "review_id",
]
MIN_WINDOW_TRADES = 30


def _utc(value):
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone required")
    return parsed.astimezone(timezone.utc)


def _metric_set(rows):
    values = [row["net_pnl_r"] for row in rows]
    wins = sum(value for value in values if value > 0)
    losses = sum(value for value in values if value < 0)
    equity = peak = max_dd = 0.0
    for value in values:
        equity += value
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    return {
        "samples": len(values),
        "net_profit_factor": wins / abs(losses) if losses < 0 else None,
        "net_winrate_pct": sum(value > 0 for value in values) / len(values) * 100,
        "net_expectancy_r": sum(values) / len(values),
        "net_max_drawdown_r": max_dd,
        "net_total_r": sum(values),
    }


def evaluate_cost_aware_oos_csv(
    source,
    expected_sha256,
    *,
    train_end,
    validation_end,
    test_end,
    embargo_seconds=86400,
):
    result = {
        "decision": "BLOCKED",
        "windows": {},
        "issues": [],
        "source_sha256": None,
        "causal_signal_verified": False,
        "independent_provenance_verified": False,
        "runtime_promotion_allowed": False,
        "real_execution_allowed": False,
    }
    try:
        train_cut = _utc(train_end)
        validation_cut = _utc(validation_end)
        test_cut = _utc(test_end)
        if not (train_cut < validation_cut < test_cut):
            raise ValueError("window boundaries must be strictly increasing")
        if type(embargo_seconds) is not int or embargo_seconds < 0 or embargo_seconds > 31_536_000:
            raise ValueError("invalid embargo")
    except (ValueError, TypeError, OverflowError):
        result["issues"] = ["INVALID_WINDOW_CONFIGURATION"]
        return result

    snapshot = snapshot_verified_csv(source, expected_sha256, expected_columns=EXPECTED_COLUMNS)
    if not snapshot["verified"]:
        result["issues"] = ["IMMUTABLE_SNAPSHOT_REJECTED"] + snapshot["issues"]
        return result
    # The immutable reader verified the exact opened file descriptor against
    # this digest; avoid a second path-based read (TOCTOU).
    result["source_sha256"] = expected_sha256.lower()

    rows = snapshot["rows"]
    if not rows:
        result["issues"] = ["NO_TRADES"]
        return result
    if list(rows[0].keys()) != EXPECTED_COLUMNS:
        result["issues"] = ["INVALID_CSV_SCHEMA"]
        return result

    parsed = []
    seen_ids = set()
    try:
        for row in rows:
            edge_id = row["edge_id"]
            signal_id = row["signal_id"]
            review_id = row["review_id"]
            if (not edge_id or edge_id.strip() != edge_id or not signal_id
                    or signal_id.strip() != signal_id or not signal_id.strip()
                    or signal_id in seen_ids):
                raise ValueError("invalid or duplicate identifiers")
            if not review_id or review_id.strip() != review_id or not review_id.strip():
                raise ValueError("review id required")
            seen_ids.add(signal_id)
            hashes = (
                row["signal_logic_sha256"],
                row["market_data_sha256"],
                row["execution_record_sha256"],
            )
            if any(
                not isinstance(value, str) or len(value) != 64
                or any(char not in "0123456789abcdefABCDEF" for char in value)
                for value in hashes
            ):
                raise ValueError("invalid evidence hash")
            signal_time = _utc(row["signal_timestamp"])
            entry_time = _utc(row["entry_timestamp"])
            exit_time = _utc(row["exit_timestamp"])
            if not signal_time <= entry_time <= exit_time:
                raise ValueError("noncausal event chronology")
            gross = float(row["pnl_gross_r"])
            spread = float(row["spread_r"])
            slippage = float(row["slippage_r"])
            commission = float(row["commission_r"])
            numbers = (gross, spread, slippage, commission)
            if any(not math.isfinite(number) for number in numbers):
                raise ValueError("nonfinite trade value")
            if any(cost < 0 for cost in (spread, slippage, commission)):
                raise ValueError("negative execution cost")
            if any(abs(number) > 1000 for number in numbers):
                raise ValueError("trade value outside limits")
            parsed.append({
                "edge_id": edge_id,
                "signal_time": signal_time,
                "entry_time": entry_time,
                "exit_time": exit_time,
                "net_pnl_r": gross - spread - slippage - commission,
            })
    except (ValueError, TypeError, KeyError, OverflowError):
        result["issues"] = ["INVALID_TRADE_OR_PROVENANCE_METADATA"]
        return result

    if parsed != sorted(parsed, key=lambda row: row["signal_time"]):
        result["issues"] = ["NONCHRONOLOGICAL_SIGNALS"]
        return result
    if len({row["edge_id"] for row in parsed}) != 1:
        result["issues"] = ["ONE_EDGE_PER_EVALUATION_REQUIRED"]
        return result
    by_entry = sorted(parsed, key=lambda row: row["entry_time"])
    if any(
        by_entry[index]["entry_time"] < by_entry[index - 1]["exit_time"]
        for index in range(1, len(by_entry))
    ):
        result["issues"] = ["OVERLAPPING_POSITIONS_REQUIRE_SEPARATE_MODEL"]
        return result

    try:
        val_start = train_cut + timedelta(seconds=embargo_seconds)
        test_start = validation_cut + timedelta(seconds=embargo_seconds)
    except OverflowError:
        result["issues"] = ["INVALID_WINDOW_CONFIGURATION"]
        return result
    windows = {"train": [], "validation": [], "test": []}
    for row in parsed:
        if row["signal_time"] <= train_cut and row["exit_time"] <= train_cut:
            windows["train"].append(row)
        elif row["signal_time"] >= val_start and row["exit_time"] <= validation_cut:
            windows["validation"].append(row)
        elif row["signal_time"] >= test_start and row["exit_time"] <= test_cut:
            windows["test"].append(row)
        # Events in embargo gaps or crossing a boundary are purged.

    for name, window in windows.items():
        if len(window) < MIN_WINDOW_TRADES:
            result["issues"].append(name.upper() + "_INSUFFICIENT_SAMPLES")
            continue
        # Equity/drawdown follow realized exits, not signal-generation order.
        realized = sorted(window, key=lambda row: (row["exit_time"], row["signal_time"]))
        result["windows"][name] = _metric_set(realized)

    result["issues"].extend([
        "SIGNAL_CAUSALITY_NOT_INDEPENDENTLY_VERIFIED",
        "EVIDENCE_HASH_OWNERSHIP_NOT_INDEPENDENTLY_VERIFIED",
        "RESEARCH_ONLY_NO_RUNTIME_PROMOTION",
    ])
    if len(result["windows"]) == 3:
        result["decision"] = "RESEARCH_ONLY_OOS_METRICS_AVAILABLE"
    return result
