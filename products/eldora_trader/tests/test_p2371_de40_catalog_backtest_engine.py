from pathlib import Path
import csv

from app.runtime.p2371_de40_catalog_backtest_engine import (
    load_candles,
    eval_candidate,
)


def make_csv(path: Path, n: int = 800):
    price = 10000.0
    rows = []
    for i in range(n):
        price += 2 if i % 4 else -1
        rows.append({
            "time": f"2026-01-01 09:{i%60:02d}:00",
            "open": price - 1,
            "high": price + 6,
            "low": price - 6,
            "close": price,
        })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time", "open", "high", "low", "close"], delimiter=";")
        w.writeheader()
        w.writerows(rows)


def test_eval_candidate_returns_metrics(tmp_path):
    p = tmp_path / "DE40_M5_csv"
    make_csv(p)

    candles = load_candles(p)
    candidate = {
        "symbol": "DE40",
        "family": "PULLBACK",
        "variant": "EMA_PULLBACK",
        "profile": "INTRADAY",
        "timeframe": "M5",
        "target_frequency": "1_WINNING_OPPORTUNITY_PER_DAY_TARGET",
        "min_rr": "2.0",
        "preferred_rr": "3.0",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "status": "CATALOGED_FOR_BACKTEST",
        "warning": "TARGET_FREQUENCY_IS_DISCOVERY_GOAL_NOT_WIN_PROMISE",
    }

    row = eval_candidate(candidate, candles)
    assert row["mode"] == "PAPER_ONLY"
    assert row["real_orders"] == "FORBIDDEN"
    assert "expectancy_r" in row
    assert "profit_factor" in row
    assert "decision" in row
