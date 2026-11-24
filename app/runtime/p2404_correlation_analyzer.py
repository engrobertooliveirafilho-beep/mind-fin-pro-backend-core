"""P2404 offline edge correlation analyzer; never authorizes runtime execution."""
from __future__ import annotations
from collections.abc import Mapping
from itertools import combinations
from math import isfinite
from statistics import StatisticsError, correlation
from typing import Any

MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"
REQUIRED_SCHEMA = ("edge_id", "timestamp", "signal", "pnl_r", "entry_time", "exit_time", "holding_bars")

class CorrelationInputError(ValueError):
    """Raised when source series cannot be trusted for correlation analysis."""

def safety_contract() -> dict[str, Any]:
    return {"mode": MODE, "real_orders": REAL_ORDERS, "ftmo_real": FTMO_REAL,
            "real_execution_allowed": False, "runtime_allowed": False,
            "purpose": "offline_edge_correlation_analysis"}

def runtime_allowed() -> bool:
    return False

def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise CorrelationInputError(f"{field}: boolean is not numeric evidence")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise CorrelationInputError(f"{field}: finite numeric value required") from exc
    if not isfinite(result):
        raise CorrelationInputError(f"{field}: finite numeric value required")
    return result

def _validate_rows(rows: Any) -> dict[str, dict[str, float]]:
    if not isinstance(rows, (list, tuple)) or not rows:
        raise CorrelationInputError("rows: non-empty list required")
    series: dict[str, dict[str, float]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise CorrelationInputError(f"row[{index}]: mapping required")
        missing = [key for key in REQUIRED_SCHEMA if key not in row]
        if missing:
            raise CorrelationInputError(f"row[{index}]: missing fields {','.join(missing)}")
        edge_id, timestamp = row["edge_id"], row["timestamp"]
        if not isinstance(edge_id, str) or not edge_id.strip():
            raise CorrelationInputError(f"row[{index}]: invalid edge_id")
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise CorrelationInputError(f"row[{index}]: invalid timestamp")
        for field in ("signal", "entry_time", "exit_time"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise CorrelationInputError(f"row[{index}]: invalid {field}")
        holding = _finite(row["holding_bars"], f"row[{index}].holding_bars")
        if holding < 0 or not holding.is_integer():
            raise CorrelationInputError(f"row[{index}]: holding_bars must be a non-negative integer")
        pnl = _finite(row["pnl_r"], f"row[{index}].pnl_r")
        edge_series = series.setdefault(edge_id, {})
        if timestamp in edge_series:
            raise CorrelationInputError(f"duplicate edge/timestamp: {edge_id}/{timestamp}")
        edge_series[timestamp] = pnl
    if len(series) < 2:
        raise CorrelationInputError("at least two distinct edge series are required")
    return series

def analyze_correlation(rows: Any, *, min_overlap: int = 30, threshold: float = 0.75) -> dict[str, Any]:
    """Pairwise Pearson correlation on exact shared timestamps; missing values are never zero-filled."""
    if isinstance(min_overlap, bool) or not isinstance(min_overlap, int) or min_overlap < 3:
        raise CorrelationInputError("min_overlap must be an integer >= 3")
    threshold_value = _finite(threshold, "threshold")
    if not 0.0 <= threshold_value <= 1.0:
        raise CorrelationInputError("threshold must be within 0..1")
    series = _validate_rows(rows)
    pair_results, redundant_pairs, unmeasured_pairs = [], [], []
    for edge_a, edge_b in combinations(sorted(series), 2):
        shared = sorted(set(series[edge_a]).intersection(series[edge_b]))
        if len(shared) < min_overlap:
            result = {"edge_a": edge_a, "edge_b": edge_b, "overlap": len(shared),
                      "correlation": None, "status": "UNMEASURED",
                      "reason": "INSUFFICIENT_SHARED_TIMESTAMPS", "redundant": None}
            unmeasured_pairs.append(result)
        else:
            values_a = [series[edge_a][stamp] for stamp in shared]
            values_b = [series[edge_b][stamp] for stamp in shared]
            try:
                value = float(correlation(values_a, values_b))
            except StatisticsError:
                value = None
            if value is None or not isfinite(value):
                result = {"edge_a": edge_a, "edge_b": edge_b, "overlap": len(shared),
                          "correlation": None, "status": "UNMEASURED",
                          "reason": "CONSTANT_OR_UNDEFINED_SERIES", "redundant": None}
                unmeasured_pairs.append(result)
            else:
                redundant = abs(value) >= threshold_value
                result = {"edge_a": edge_a, "edge_b": edge_b, "overlap": len(shared),
                          "correlation": round(value, 8), "status": "MEASURED",
                          "reason": "ABS_CORRELATION_AT_OR_ABOVE_THRESHOLD" if redundant else "BELOW_CORRELATION_THRESHOLD",
                          "redundant": redundant}
                if redundant:
                    redundant_pairs.append(result)
        pair_results.append(result)
    total_pairs = len(pair_results)
    measured_pairs = total_pairs - len(unmeasured_pairs)
    complete = measured_pairs == total_pairs
    return {
        "mission": "P2404_CORRELATION_ANALYZER",
        "status": "MEASURED" if complete else "INCOMPLETE",
        "reason": "ALL_PAIRS_MEASURED" if complete else "ONE_OR_MORE_PAIRS_UNMEASURED",
        "edges": len(series), "pairs": total_pairs, "measured_pairs": measured_pairs,
        "unmeasured_pairs": len(unmeasured_pairs), "redundant_pairs": len(redundant_pairs),
        "correlation_threshold": threshold_value, "min_overlap": min_overlap,
        "pair_results": pair_results, "redundant_pair_details": redundant_pairs,
        "unmeasured_pair_details": unmeasured_pairs,
        "portfolio_diversity_certified": False, "runtime_allowed": False,
        "mode": MODE, "real_orders": REAL_ORDERS, "ftmo_real": FTMO_REAL,
        "real_execution_allowed": False,
    }
