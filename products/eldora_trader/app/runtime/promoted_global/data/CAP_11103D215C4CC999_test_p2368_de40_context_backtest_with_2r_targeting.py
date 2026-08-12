from pathlib import Path
import csv

from app.runtime.p2368_de40_context_backtest_with_2r_targeting import (
    load_candles,
    regime_context,
    simulate_trade,
    summarize_context,
)


def make_csv(path: Path, n: int = 700):
    rows = []
    price = 10000.0
    for i in range(n):
        price += 2.0 if i % 3 else -0.5
        rows.append({
            "time": f"2026-01-01 {8 + (i // 12) % 8:02d}:{(i * 5) % 60:02d}:00",
            "open": price - 1,
            "high": price + 6,
            "low": price - 6,
            "close": price,
        })
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time", "open", "high", "low", "close"])
        w.writeheader()
        w.writerows(rows)


def test_load_candles_and_context(tmp_path):
    p = tmp_path / "m5.csv"
    make_csv(p)
    candles = load_candles(p)
    assert len(candles) == 700
    ctx = regime_context(candles, 150)
    assert ctx is not None
    assert ctx[0].startswith("DE40_M5::")


def test_simulate_trade_and_summary(tmp_path):
    p = tmp_path / "m5.csv"
    make_csv(p)
    candles = load_candles(p)
    trade = simulate_trade(candles, 150, 1, risk_points=10, rr=2.0)
    assert trade is not None
    assert trade["rr"] == 2.0
    rows = []
    for i in range(35):
        t = dict(trade)
        t["context"] = "DE40_M5::EUROPE_OPEN::TREND_UP::MID_VOL"
        t["result_r"] = 1.5 if i % 2 == 0 else -1.0
        rows.append(t)
    summary = summarize_context(rows, min_samples=30)
    assert len(summary) == 1
    assert summary[0]["samples"] == 35
    assert summary[0]["profit_factor"] > 0
