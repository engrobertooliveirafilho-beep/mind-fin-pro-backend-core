from pathlib import Path
import csv

from app.runtime.p2369_de40_multitimeframe_edge_discovery_loop import (
    load_candles,
    evaluate_strategy,
)


def make_csv(path: Path, n: int = 700):
    rows = []
    price = 10000.0

    for i in range(n):
        price += 3 if i % 4 else -1
        rows.append({
            "time": f"2026-01-01 {8 + (i // 12) % 8:02d}:{(i * 5) % 60:02d}:00",
            "open": price - 2,
            "high": price + 8,
            "low": price - 8,
            "close": price,
        })

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time", "open", "high", "low", "close"], delimiter=";")
        w.writeheader()
        w.writerows(rows)


def test_load_semicolon_csv(tmp_path):
    p = tmp_path / "DE40_M5_csv"
    make_csv(p)

    candles = load_candles(p)
    assert len(candles) == 700
    assert candles[0].close > 0


def test_evaluate_strategy_returns_metrics(tmp_path):
    p = tmp_path / "DE40_M5_csv"
    make_csv(p)

    candles = load_candles(p)
    row = evaluate_strategy(
        candles=candles,
        timeframe="M5",
        strategy="EMA_CROSS",
        fast=9,
        slow=34,
        rr=2.0,
        hold=36,
        step=5,
    )

    assert row["symbol"] == "DE40"
    assert row["timeframe"] == "M5"
    assert row["rr"] == 2.0
    assert "decision" in row
    assert "expectancy_r" in row
    assert "profit_factor" in row
