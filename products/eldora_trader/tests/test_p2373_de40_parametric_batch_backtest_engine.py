from pathlib import Path
import csv

from app.runtime.p2373_de40_parametric_batch_backtest_engine import (
    load_candles,
    evaluate,
)


def make_csv(path: Path, n: int = 900):
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


def test_evaluate_parametric_candidate(tmp_path):
    p = tmp_path / "DE40_M5_csv"
    make_csv(p)

    candles = load_candles(p)
    candidate = {
        "symbol": "DE40",
        "family": "PULLBACK",
        "variant": "EMA_PULLBACK",
        "profile": "INTRADAY",
        "timeframe": "M5",
        "rr": "2.0",
        "hold": "24",
        "atr_multiplier": "1.0",
        "session_filter": "ALL_ACTIVE",
        "fast": "9",
        "slow": "34",
        "pullback_depth": "0.5",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
    }

    row = evaluate(candidate, candles)

    assert row["mode"] == "PAPER_ONLY"
    assert row["real_orders"] == "FORBIDDEN"
    assert "expectancy_r" in row
    assert "profit_factor" in row
    assert "decision" in row
