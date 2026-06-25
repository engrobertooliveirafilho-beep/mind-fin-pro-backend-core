from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List


MISSION = "P2372_DE40_PARAMETRIC_STRATEGY_VARIATION_ENGINE"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


def sniff_delimiter(path: Path) -> str:
    first = path.read_text(encoding="utf-8-sig", errors="ignore")[:2048].splitlines()[0]
    return ";" if first.count(";") > first.count(",") else ","


def load_csv(path: Path) -> List[Dict]:
    delimiter = sniff_delimiter(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def base_param_grid(family: str, profile: str) -> Dict:
    rr_values = [2.0, 3.0, 5.0]

    if profile == "SCALP":
        hold_values = [12, 24, 36]
        session_filters = ["EUROPE_OPEN", "US_OVERLAP", "ALL_ACTIVE"]
    elif profile == "INTRADAY":
        hold_values = [24, 36, 72]
        session_filters = ["EUROPE_OPEN", "EUROPE_MID", "US_OVERLAP", "ALL_ACTIVE"]
    else:
        hold_values = [20, 40, 80]
        session_filters = ["ALL"]

    grid = {
        "rr_values": rr_values,
        "hold_values": hold_values,
        "session_filters": session_filters,
        "atr_multipliers": [0.8, 1.0, 1.25, 1.5],
        "volatility_filters": ["LOW_MID_HIGH", "MID_HIGH_ONLY", "HIGH_ONLY"],
        "trend_filters": ["NONE", "SMA_20_50", "SMA_50_100"],
    }

    if family == "TREND_FOLLOWING":
        grid.update({
            "fast_values": [5, 9, 13, 20],
            "slow_values": [34, 55, 89],
            "entry_buffers": [0.0, 0.25, 0.5],
        })

    elif family == "PULLBACK":
        grid.update({
            "fast_values": [9, 13, 20],
            "slow_values": [34, 55, 89],
            "pullback_depths": [0.25, 0.5, 0.75, 1.0],
            "confirmation_modes": ["CLOSE_RECLAIM", "WICK_REJECT", "ENGULF"],
        })

    elif family == "CORRECTION":
        grid.update({
            "correction_depths": [0.382, 0.5, 0.618, 0.786],
            "structure_lookbacks": [20, 50, 100],
            "confirmation_modes": ["BREAK_MINOR_STRUCTURE", "CLOSE_RECLAIM", "ATR_REACTION"],
        })

    elif family == "REVERSAL":
        grid.update({
            "rsi_thresholds": [20, 25, 30, 70, 75, 80],
            "lookbacks": [14, 20, 34],
            "reversal_strength": [0.5, 0.75, 1.0, 1.5],
            "confirmation_modes": ["CANDLE_CLOSE", "WICK_REJECTION", "STRUCTURE_SHIFT"],
        })

    elif family == "COUNTER_TREND":
        grid.update({
            "rsi_thresholds": [20, 25, 30, 70, 75, 80],
            "extension_atr": [1.0, 1.5, 2.0, 2.5],
            "mean_targets": ["VWAP_PROXY", "SMA20", "SMA50"],
        })

    elif family == "BREAKOUT":
        grid.update({
            "lookbacks": [10, 20, 50, 100],
            "breakout_buffers": [0.0, 0.25, 0.5, 1.0],
            "confirmation_modes": ["CLOSE_BREAK", "BODY_BREAK", "ATR_EXPANSION"],
        })

    elif family == "MEAN_REVERSION":
        grid.update({
            "zscore_thresholds": [1.0, 1.5, 2.0, 2.5],
            "mean_windows": [20, 50, 100],
            "reversion_targets": ["SMA20", "SMA50", "MID_RANGE"],
        })

    elif family == "LIQUIDITY":
        grid.update({
            "sweep_lookbacks": [10, 20, 50],
            "sweep_depth_atr": [0.1, 0.25, 0.5, 0.75],
            "confirmation_modes": ["CLOSE_BACK_INSIDE", "WICK_REJECTION", "STRUCTURE_SHIFT"],
        })

    elif family == "SMART_MONEY":
        grid.update({
            "structure_lookbacks": [20, 50, 100],
            "imbalance_depth": [0.25, 0.5, 0.75],
            "confirmation_modes": ["BOS", "CHOCH", "FVG_RETEST", "ORDER_BLOCK_REACTION"],
        })

    elif family == "SESSION":
        grid.update({
            "opening_range_minutes": [15, 30, 60],
            "session_modes": ["OPEN_DRIVE", "REVERSAL", "FADE"],
            "breakout_buffers": [0.0, 0.25, 0.5],
        })

    elif family == "VOLATILITY":
        grid.update({
            "atr_windows": [14, 20, 34],
            "compression_windows": [20, 50, 100],
            "expansion_thresholds": [0.8, 1.0, 1.25, 1.5],
        })

    return grid


def expand_candidate(row: Dict) -> List[Dict]:
    family = row["family"]
    profile = row["profile"]
    grid = base_param_grid(family, profile)

    out: List[Dict] = []

    for rr in grid["rr_values"]:
        for hold in grid["hold_values"]:
            for session in grid["session_filters"]:
                for atr_mult in grid["atr_multipliers"]:
                    for vol_filter in grid["volatility_filters"]:
                        for trend_filter in grid["trend_filters"]:

                            base = dict(row)
                            base.update({
                                "rr": rr,
                                "hold": hold,
                                "session_filter": session,
                                "atr_multiplier": atr_mult,
                                "volatility_filter": vol_filter,
                                "trend_filter": trend_filter,
                                "mode": MODE,
                                "real_orders": REAL_ORDERS,
                                "ftmo_real": FTMO_REAL,
                                "status": "PARAMETRIC_CANDIDATE",
                            })

                            if family in ["TREND_FOLLOWING"]:
                                for fast in grid["fast_values"]:
                                    for slow in grid["slow_values"]:
                                        if fast >= slow:
                                            continue
                                        for buffer in grid["entry_buffers"]:
                                            x = dict(base)
                                            x.update({"fast": fast, "slow": slow, "entry_buffer": buffer})
                                            out.append(x)

                            elif family == "PULLBACK":
                                for fast in grid["fast_values"]:
                                    for slow in grid["slow_values"]:
                                        if fast >= slow:
                                            continue
                                        for depth in grid["pullback_depths"]:
                                            for confirm in grid["confirmation_modes"]:
                                                x = dict(base)
                                                x.update({"fast": fast, "slow": slow, "pullback_depth": depth, "confirmation_mode": confirm})
                                                out.append(x)

                            elif family == "CORRECTION":
                                for depth in grid["correction_depths"]:
                                    for lookback in grid["structure_lookbacks"]:
                                        for confirm in grid["confirmation_modes"]:
                                            x = dict(base)
                                            x.update({"correction_depth": depth, "structure_lookback": lookback, "confirmation_mode": confirm})
                                            out.append(x)

                            elif family == "REVERSAL":
                                for rsi_t in grid["rsi_thresholds"]:
                                    for lookback in grid["lookbacks"]:
                                        for strength in grid["reversal_strength"]:
                                            for confirm in grid["confirmation_modes"]:
                                                x = dict(base)
                                                x.update({"rsi_threshold": rsi_t, "lookback": lookback, "reversal_strength": strength, "confirmation_mode": confirm})
                                                out.append(x)

                            elif family == "COUNTER_TREND":
                                for rsi_t in grid["rsi_thresholds"]:
                                    for ext in grid["extension_atr"]:
                                        for mean_target in grid["mean_targets"]:
                                            x = dict(base)
                                            x.update({"rsi_threshold": rsi_t, "extension_atr": ext, "mean_target": mean_target})
                                            out.append(x)

                            elif family == "BREAKOUT":
                                for lookback in grid["lookbacks"]:
                                    for buffer in grid["breakout_buffers"]:
                                        for confirm in grid["confirmation_modes"]:
                                            x = dict(base)
                                            x.update({"lookback": lookback, "breakout_buffer": buffer, "confirmation_mode": confirm})
                                            out.append(x)

                            elif family == "MEAN_REVERSION":
                                for z in grid["zscore_thresholds"]:
                                    for window in grid["mean_windows"]:
                                        for target in grid["reversion_targets"]:
                                            x = dict(base)
                                            x.update({"zscore_threshold": z, "mean_window": window, "reversion_target": target})
                                            out.append(x)

                            elif family == "LIQUIDITY":
                                for lookback in grid["sweep_lookbacks"]:
                                    for depth in grid["sweep_depth_atr"]:
                                        for confirm in grid["confirmation_modes"]:
                                            x = dict(base)
                                            x.update({"sweep_lookback": lookback, "sweep_depth_atr": depth, "confirmation_mode": confirm})
                                            out.append(x)

                            elif family == "SMART_MONEY":
                                for lookback in grid["structure_lookbacks"]:
                                    for imbalance in grid["imbalance_depth"]:
                                        for confirm in grid["confirmation_modes"]:
                                            x = dict(base)
                                            x.update({"structure_lookback": lookback, "imbalance_depth": imbalance, "confirmation_mode": confirm})
                                            out.append(x)

                            elif family == "SESSION":
                                for minutes in grid["opening_range_minutes"]:
                                    for mode in grid["session_modes"]:
                                        for buffer in grid["breakout_buffers"]:
                                            x = dict(base)
                                            x.update({"opening_range_minutes": minutes, "session_mode": mode, "breakout_buffer": buffer})
                                            out.append(x)

                            elif family == "VOLATILITY":
                                for atr_window in grid["atr_windows"]:
                                    for compression in grid["compression_windows"]:
                                        for threshold in grid["expansion_thresholds"]:
                                            x = dict(base)
                                            x.update({"atr_window": atr_window, "compression_window": compression, "expansion_threshold": threshold})
                                            out.append(x)

    return out


def generate(catalog_path: Path, outdir: Path, max_per_base: int = 300) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    catalog = load_csv(catalog_path)

    rows: List[Dict] = []
    family_counts = {}

    for row in catalog:
        if row["timeframe"] == "M2":
            continue

        expanded = expand_candidate(row)
        if max_per_base > 0:
            expanded = expanded[:max_per_base]

        rows.extend(expanded)
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + len(expanded)

    out_csv = outdir / "de40_parametric_strategy_candidates.csv"
    summary_json = outdir / "summary.json"

    fieldnames = sorted({k for r in rows for k in r.keys()})

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "source_catalog": str(catalog_path),
        "base_catalog_rows": len(catalog),
        "m2_policy": "SKIPPED_NO_REAL_M2_DATASET",
        "parametric_candidates": len(rows),
        "family_counts": family_counts,
        "outputs": {
            "parametric_candidates": str(out_csv),
            "summary_json": str(summary_json),
        },
        "status": "CERTIFIED",
        "certification": "P2372_DE40_PARAMETRIC_STRATEGY_VARIATION_ENGINE_CERTIFIED",
        "next": "P2373_DE40_PARAMETRIC_BATCH_BACKTEST_ENGINE",
        "warning": "TARGET_FREQUENCY_IS_DISCOVERY_OBJECTIVE_NOT_WIN_PROMISE",
    }

    summary_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max-per-base", type=int, default=300)
    args = p.parse_args()

    result = generate(Path(args.catalog), Path(args.outdir), args.max_per_base)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
