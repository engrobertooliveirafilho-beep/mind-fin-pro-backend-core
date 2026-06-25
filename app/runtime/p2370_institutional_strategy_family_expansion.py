from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List


MISSION = "P2370_DE40_INSTITUTIONAL_STRATEGY_FAMILY_EXPANSION"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


STRATEGY_FAMILIES: List[Dict] = [
    {
        "family": "TREND_FOLLOWING",
        "variants": [
            "EMA_TREND_CONTINUATION",
            "SMA_TREND_CONTINUATION",
            "VWAP_TREND_CONTINUATION",
            "DONCHIAN_TREND_BREAK",
            "SUPERTREND_CONTINUATION",
        ],
        "profiles": ["SCALP", "INTRADAY", "SWING"],
    },
    {
        "family": "PULLBACK",
        "variants": [
            "EMA_PULLBACK",
            "VWAP_PULLBACK",
            "FIBONACCI_PULLBACK",
            "STRUCTURE_PULLBACK",
            "ATR_PULLBACK",
        ],
        "profiles": ["SCALP", "INTRADAY", "SWING"],
    },
    {
        "family": "CORRECTION",
        "variants": [
            "TREND_CORRECTION_ENTRY",
            "ABC_CORRECTION",
            "SHALLOW_CORRECTION",
            "DEEP_CORRECTION",
            "CORRECTION_TO_VALUE_AREA",
        ],
        "profiles": ["INTRADAY", "SWING"],
    },
    {
        "family": "REVERSAL",
        "variants": [
            "RSI_REVERSAL",
            "DIVERGENCE_REVERSAL",
            "CLIMAX_REVERSAL",
            "EXHAUSTION_REVERSAL",
            "DOUBLE_TOP_BOTTOM_REVERSAL",
        ],
        "profiles": ["SCALP", "INTRADAY", "SWING"],
    },
    {
        "family": "COUNTER_TREND",
        "variants": [
            "VWAP_COUNTER_TREND",
            "BOLLINGER_COUNTER_TREND",
            "RSI_EXTREME_COUNTER_TREND",
            "ATR_EXHAUSTION_COUNTER_TREND",
            "LIQUIDITY_COUNTER_TREND",
        ],
        "profiles": ["SCALP", "INTRADAY"],
    },
    {
        "family": "BREAKOUT",
        "variants": [
            "OPENING_RANGE_BREAKOUT",
            "SESSION_BREAKOUT",
            "DONCHIAN_BREAKOUT",
            "ATR_EXPANSION_BREAKOUT",
            "HIGH_LOW_BREAKOUT",
        ],
        "profiles": ["SCALP", "INTRADAY", "SWING"],
    },
    {
        "family": "MEAN_REVERSION",
        "variants": [
            "VWAP_REVERSION",
            "BOLLINGER_REVERSION",
            "ZSCORE_REVERSION",
            "RSI_MEAN_REVERSION",
            "VALUE_AREA_REVERSION",
        ],
        "profiles": ["SCALP", "INTRADAY"],
    },
    {
        "family": "LIQUIDITY",
        "variants": [
            "LIQUIDITY_SWEEP_REVERSAL",
            "STOP_HUNT_REVERSAL",
            "FAKE_BREAKOUT_REVERSAL",
            "SESSION_HIGH_SWEEP",
            "SESSION_LOW_SWEEP",
        ],
        "profiles": ["SCALP", "INTRADAY"],
    },
    {
        "family": "SMART_MONEY",
        "variants": [
            "BOS_CONTINUATION",
            "CHOCH_REVERSAL",
            "FAIR_VALUE_GAP_CONTINUATION",
            "ORDER_BLOCK_REACTION",
            "BREAKER_BLOCK_REACTION",
        ],
        "profiles": ["INTRADAY", "SWING"],
    },
    {
        "family": "SESSION",
        "variants": [
            "LONDON_OPEN_DRIVE",
            "NEW_YORK_OPEN_DRIVE",
            "LONDON_REVERSAL",
            "NEW_YORK_REVERSAL",
            "ASIA_FADE",
        ],
        "profiles": ["SCALP", "INTRADAY"],
    },
    {
        "family": "VOLATILITY",
        "variants": [
            "ATR_COMPRESSION_EXPANSION",
            "VOLATILITY_CYCLE_EXPANSION",
            "LOW_VOL_BREAKOUT",
            "HIGH_VOL_REVERSAL",
            "RANGE_EXPANSION",
        ],
        "profiles": ["SCALP", "INTRADAY", "SWING"],
    },
]


OBJECTIVE_PROFILES = [
    {
        "profile": "SCALP",
        "timeframes": ["M1", "M2"],
        "target_frequency": "2_WINNING_OPPORTUNITIES_PER_DAY_TARGET",
        "min_rr": 2.0,
        "preferred_rr": 3.0,
        "permission": "PAPER_ONLY_CANDIDATE_DISCOVERY",
    },
    {
        "profile": "INTRADAY",
        "timeframes": ["M2", "M5", "M15"],
        "target_frequency": "1_WINNING_OPPORTUNITY_PER_DAY_TARGET",
        "min_rr": 2.0,
        "preferred_rr": 3.0,
        "permission": "PAPER_ONLY_CANDIDATE_DISCOVERY",
    },
    {
        "profile": "SWING",
        "timeframes": ["H1", "H4", "D1"],
        "target_frequency": "1_WINNING_OPPORTUNITY_PER_MONTH_TARGET",
        "min_rr": 2.0,
        "preferred_rr": 5.0,
        "permission": "PAPER_ONLY_CANDIDATE_DISCOVERY",
    },
]


def build_catalog() -> List[Dict]:
    rows: List[Dict] = []

    for family in STRATEGY_FAMILIES:
        for variant in family["variants"]:
            for profile in OBJECTIVE_PROFILES:
                if profile["profile"] not in family["profiles"]:
                    continue

                for timeframe in profile["timeframes"]:
                    rows.append(
                        {
                            "symbol": "DE40",
                            "family": family["family"],
                            "variant": variant,
                            "profile": profile["profile"],
                            "timeframe": timeframe,
                            "target_frequency": profile["target_frequency"],
                            "min_rr": profile["min_rr"],
                            "preferred_rr": profile["preferred_rr"],
                            "mode": MODE,
                            "real_orders": REAL_ORDERS,
                            "ftmo_real": FTMO_REAL,
                            "status": "CATALOGED_FOR_BACKTEST",
                            "warning": "TARGET_FREQUENCY_IS_DISCOVERY_GOAL_NOT_WIN_PROMISE",
                        }
                    )

    return rows


def write_outputs(outdir: Path) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    rows = build_catalog()

    catalog_csv = outdir / "de40_institutional_strategy_family_catalog.csv"
    profiles_json = outdir / "de40_objective_profiles.json"
    summary_json = outdir / "summary.json"

    with catalog_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    profiles_json.write_text(
        json.dumps(
            {
                "mission": MISSION,
                "mode": MODE,
                "real_orders": REAL_ORDERS,
                "ftmo_real": FTMO_REAL,
                "objective_profiles": OBJECTIVE_PROFILES,
                "strategy_families": STRATEGY_FAMILIES,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    family_count = len(STRATEGY_FAMILIES)
    variant_count = sum(len(x["variants"]) for x in STRATEGY_FAMILIES)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "families": family_count,
        "variants": variant_count,
        "catalog_candidates": len(rows),
        "profiles": [x["profile"] for x in OBJECTIVE_PROFILES],
        "outputs": {
            "catalog": str(catalog_csv),
            "profiles": str(profiles_json),
            "summary_json": str(summary_json),
        },
        "status": "CERTIFIED",
        "certification": "P2370_INSTITUTIONAL_STRATEGY_FAMILY_EXPANSION_CERTIFIED",
        "next": "P2371_DE40_CATALOG_BACKTEST_ENGINE",
    }

    summary_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", required=True)
    args = parser.parse_args()

    result = write_outputs(Path(args.outdir))
    print(json.dumps(result, indent=2))
