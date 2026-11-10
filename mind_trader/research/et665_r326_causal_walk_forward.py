"""ET665 R327 — fail-closed empirical metrics from a hash-pinned CSV.

Research only. This module does not establish causal provenance, include trading
costs, certify out-of-sample performance, or authorize runtime promotion.
"""
import csv
import hashlib
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

MAX_SOURCE_BYTES = 64 * 1024 * 1024


def evaluate_csv(path, *, expected_sha256=None):
    result = {
        "decision": "BLOCKED",
        "runtime_promotion_allowed": False,
        "real_execution_allowed": False,
        "source_sha256": None,
        "issues": [],
        "edges": {},
    }
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        result["issues"].append("INVALID_SOURCE")
        return result
    try:
        if p.stat().st_size > MAX_SOURCE_BYTES:
            result["issues"].append("SOURCE_TOO_LARGE")
            return result
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        result["issues"].append("UNREADABLE_OR_INVALID_SOURCE")
        return result
    result["source_sha256"] = digest
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        result["issues"].append("EXPECTED_SOURCE_SHA256_REQUIRED")
        return result
    if digest.lower() != expected_sha256.lower():
        result["issues"].append("SOURCE_SHA256_MISMATCH")
        return result

    try:
        with p.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames != ["edge_id", "timestamp", "pnl_r"]:
                result["issues"].append("INVALID_HEADER")
                return result
            trades = defaultdict(list)
            seen = set()
            for i, row in enumerate(reader):
                if i >= 100_000 or None in row or None in row.values():
                    result["issues"].append("INVALID_ROWS")
                    return result
                edge = row["edge_id"]
                if not edge or edge.strip() != edge:
                    result["issues"].append("INVALID_EDGE_ID")
                    return result
                stamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
                if stamp.tzinfo is None or stamp.utcoffset() is None:
                    result["issues"].append("TIMEZONE_REQUIRED")
                    return result
                stamp = stamp.astimezone(timezone.utc)
                pnl = float(row["pnl_r"])
                if not math.isfinite(pnl) or abs(pnl) > 1000:
                    result["issues"].append("INVALID_TRADE")
                    return result
                key = (edge, stamp)
                if key in seen:
                    result["issues"].append("DUPLICATE_EDGE_TIMESTAMP")
                    return result
                seen.add(key)
                trades[edge].append((stamp, pnl))
    except (OSError, ValueError, TypeError, UnicodeError, csv.Error, OverflowError):
        result["issues"].append("UNREADABLE_OR_INVALID_SOURCE")
        return result

    if not trades:
        result["issues"].append("NO_TRADES")
        return result

    for edge, data in trades.items():
        if data != sorted(data, key=lambda item: item[0]):
            result["issues"].append("NONCHRONOLOGICAL_TRADES")
            return result
        n = len(data)
        if n < 30:
            result["edges"][edge] = {
                "decision": "BLOCKED_INSUFFICIENT_SAMPLES",
                "samples": n,
            }
            continue
        values = [pnl for _, pnl in data]
        wins = [pnl for pnl in values if pnl > 0]
        losses = [pnl for pnl in values if pnl < 0]
        pf = sum(wins) / abs(sum(losses)) if losses else None
        winrate = len(wins) / n * 100
        expectancy = sum(values) / n
        equity = peak = drawdown = 0.0
        for pnl in values:
            equity += pnl
            peak = max(peak, equity)
            drawdown = max(drawdown, peak - equity)
        windows = [data[n*k//5:n*(k+1)//5] for k in range(5)]
        positive_windows = sum(sum(pnl for _, pnl in window) > 0 for window in windows)
        result["edges"][edge] = {
            "samples": n,
            "pf": pf,
            "winrate": winrate,
            "expectancy": expectancy,
            "max_dd_r": drawdown,
            "positive_windows": positive_windows,
            "research_gates_pass": bool(
                pf is not None and pf >= 1.5 and winrate >= 45
                and expectancy > 0 and drawdown <= 12 and positive_windows >= 4
            ),
            "decision": "RESEARCH_ONLY_NOT_CERTIFIED",
        }

    result["issues"].extend([
        "CAUSAL_PROVENANCE_NOT_INDEPENDENTLY_VERIFIED",
        "OUT_OF_SAMPLE_VALIDATION_NOT_ESTABLISHED",
        "TRADING_COSTS_NOT_INCLUDED",
        "RUNTIME_PROMOTION_FORBIDDEN",
    ])
    return result
