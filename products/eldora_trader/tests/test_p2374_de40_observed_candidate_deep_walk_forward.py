from pathlib import Path
import csv

from app.runtime.p2374_de40_observed_candidate_deep_walk_forward import (
    load_candles,
    walk_forward,
)


def make_csv(path: Path, n: int = 1000):
    price = 10000.0
    rows = []
    for i in range(n):
        price += 2 if i % 4 else -1
        rows.append({
            "time": f"2026-01-01 {8 + (i // 60) % 9:02d}:{i%60:02d}:00",
            "open": price - 1,
            "high": price + 8,
            "low": price - 8,
            "close": price,
        })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time", "open", "high", "low", "close"], delimiter=";")
        w.writeheader()
        w.writerows(rows)


def test_walk_forward_outputs_segments(tmp_path):
    p = tmp_path / "DE40_M5_csv"
    make_csv(p)
    candles = load_candles(p)

    candidate = {
        "symbol": "DE40",
        "family": "TREND_FOLLOWING",
        "variant": "EMA_TREND_CONTINUATION",
        "profile": "INTRADAY",
        "timeframe": "M5",
        "rr": "2.0",
        "hold": "24",
        "atr_multiplier": "1.0",
        "session_filter": "ALL_ACTIVE",
        "fast": "9",
        "slow": "34",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

    row = walk_forward(candidate, candles)

    assert row["mode"] == "PAPER_ONLY"
    assert row["real_orders"] == "FORBIDDEN"
    assert "train_expectancy_r" in row
    assert "validation_expectancy_r" in row
    assert "test_expectancy_r" in row
    assert "walk_forward_decision" in row
