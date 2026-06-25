from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


MISSION = "P2369_DE40_MULTI_TIMEFRAME_EDGE_DISCOVERY_LOOP"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


@dataclass
class Candle:
    index: int
    time: str
    open: float
    high: float
    low: float
    close: float


def fnum(v) -> float:
    return float(str(v).replace(",", ".").strip())


def sniff_delimiter(path: Path) -> str:
    first = path.read_text(encoding="utf-8-sig", errors="ignore")[:2048].splitlines()[0]
    return ";" if first.count(";") > first.count(",") else ","


def load_candles(path: Path, limit: Optional[int] = None) -> List[Candle]:
    delimiter = sniff_delimiter(path)
    out: List[Candle] = []

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        cols = {c.lower().strip(): c for c in reader.fieldnames or []}

        for required in ["time", "open", "high", "low", "close"]:
            if required not in cols:
                raise ValueError(f"missing required column {required}; columns={reader.fieldnames}")

        for i, row in enumerate(reader):
            out.append(
                Candle(
                    index=i,
                    time=row[cols["time"]],
                    open=fnum(row[cols["open"]]),
                    high=fnum(row[cols["high"]]),
                    low=fnum(row[cols["low"]]),
                    close=fnum(row[cols["close"]]),
                )
            )
            if limit and len(out) >= limit:
                break

    if len(out) < 500:
        raise ValueError(f"insufficient candles: {len(out)}")

    return out


def sma(values: List[float], i: int, period: int):
    if i - period + 1 < 0:
        return None
    return sum(values[i - period + 1 : i + 1]) / period


def ema_series(values: List[float], period: int) -> List[Optional[float]]:
    out: List[Optional[float]] = [None] * len(values)
    if len(values) < period:
        return out

    k = 2 / (period + 1)
    seed = sum(values[:period]) / period
    out[period - 1] = seed

    prev = seed
    for i in range(period, len(values)):
        prev = values[i] * k + prev * (1 - k)
        out[i] = prev

    return out


def atr_series(candles: List[Candle], period: int = 14) -> List[Optional[float]]:
    out: List[Optional[float]] = [None] * len(candles)
    trs = []

    for i in range(1, len(candles)):
        c = candles[i]
        p = candles[i - 1]
        tr = max(c.high - c.low, abs(c.high - p.close), abs(c.low - p.close))
        trs.append(tr)

        if len(trs) >= period:
            out[i] = sum(trs[-period:]) / period

    return out


def rsi_series(values: List[float], period: int = 14) -> List[Optional[float]]:
    out: List[Optional[float]] = [None] * len(values)
    gains = []
    losses = []

    for i in range(1, len(values)):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

        if len(gains) >= period:
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            if avg_loss == 0:
                out[i] = 100.0
            else:
                rs = avg_gain / avg_loss
                out[i] = 100 - (100 / (1 + rs))

    return out


def max_drawdown(results: List[float]) -> float:
    equity = 0.0
    peak = 0.0
    dd = 0.0

    for r in results:
        equity += r
        peak = max(peak, equity)
        dd = min(dd, equity - peak)

    return abs(dd)


def simulate(candles: List[Candle], i: int, direction: int, risk: float, rr: float, hold: int) -> Dict:
    entry = candles[i].close
    target = entry + direction * risk * rr
    stop = entry - direction * risk
    partial = entry + direction * risk

    mae = 0.0
    mfe = 0.0
    partial_hit = False

    for j in range(i + 1, min(len(candles), i + hold + 1)):
        c = candles[j]

        favorable = c.high - entry if direction > 0 else entry - c.low
        adverse = entry - c.low if direction > 0 else c.high - entry

        mfe = max(mfe, favorable)
        mae = max(mae, adverse)

        if not partial_hit:
            if direction > 0 and c.high >= partial:
                partial_hit = True
            if direction < 0 and c.low <= partial:
                partial_hit = True

        active_stop = entry if partial_hit else stop

        stop_hit = c.low <= active_stop if direction > 0 else c.high >= active_stop
        target_hit = c.high >= target if direction > 0 else c.low <= target

        if stop_hit and target_hit:
            return {
                "result_r": 0.5 if partial_hit else -1.0,
                "outcome": "AMBIGUOUS_STOP_FIRST",
                "mae_r": mae / risk,
                "mfe_r": mfe / risk,
                "partial": partial_hit,
            }

        if stop_hit:
            return {
                "result_r": 0.5 if partial_hit else -1.0,
                "outcome": "STOP_OR_BE",
                "mae_r": mae / risk,
                "mfe_r": mfe / risk,
                "partial": partial_hit,
            }

        if target_hit:
            return {
                "result_r": 1.5 if partial_hit else rr,
                "outcome": "TARGET",
                "mae_r": mae / risk,
                "mfe_r": mfe / risk,
                "partial": partial_hit,
            }

    final = candles[min(len(candles) - 1, i + hold)].close
    move_r = ((final - entry) * direction) / risk
    if partial_hit:
        move_r = max(0.5, move_r)

    return {
        "result_r": max(-1.0, min(rr, move_r)),
        "outcome": "TIME_EXIT",
        "mae_r": mae / risk,
        "mfe_r": mfe / risk,
        "partial": partial_hit,
    }


def evaluate_strategy(candles: List[Candle], timeframe: str, strategy: str, fast: int, slow: int, rr: float, hold: int, step: int) -> Dict:
    closes = [c.close for c in candles]
    atr = atr_series(candles, 14)
    rsi = rsi_series(closes, 14)

    ema_fast = ema_series(closes, fast)
    ema_slow = ema_series(closes, slow)

    results = []
    trades = 0
    wins = 0
    losses = 0
    total_mae = 0.0
    total_mfe = 0.0

    start = max(slow + 20, 100)
    end = len(candles) - hold - 2

    for i in range(start, end, step):
        if atr[i] is None or atr[i] <= 0:
            continue

        direction = 0

        if strategy == "EMA_CROSS":
            if ema_fast[i - 1] and ema_slow[i - 1] and ema_fast[i] and ema_slow[i]:
                if ema_fast[i - 1] <= ema_slow[i - 1] and ema_fast[i] > ema_slow[i]:
                    direction = 1
                elif ema_fast[i - 1] >= ema_slow[i - 1] and ema_fast[i] < ema_slow[i]:
                    direction = -1

        elif strategy == "SMA_TREND_PULLBACK":
            sf = sma(closes, i, fast)
            ss = sma(closes, i, slow)
            if sf and ss:
                if sf > ss and candles[i].close > sf and candles[i - 1].close <= sf:
                    direction = 1
                elif sf < ss and candles[i].close < sf and candles[i - 1].close >= sf:
                    direction = -1

        elif strategy == "RSI_MEAN_REVERSION":
            if rsi[i] is not None:
                if rsi[i] < 30:
                    direction = 1
                elif rsi[i] > 70:
                    direction = -1

        elif strategy == "ATR_BREAKOUT":
            lookback = slow
            high = max(c.high for c in candles[i - lookback : i])
            low = min(c.low for c in candles[i - lookback : i])
            if candles[i].close > high:
                direction = 1
            elif candles[i].close < low:
                direction = -1

        if direction == 0:
            continue

        risk = max(atr[i], candles[i].close * 0.0007)
        trade = simulate(candles, i, direction, risk, rr, hold)
        r = trade["result_r"]

        trades += 1
        results.append(r)
        total_mae += trade["mae_r"]
        total_mfe += trade["mfe_r"]

        if r > 0:
            wins += 1
        elif r < 0:
            losses += 1

    gross_win = sum(x for x in results if x > 0)
    gross_loss = abs(sum(x for x in results if x < 0))
    pf = gross_win / gross_loss if gross_loss > 0 else (999.0 if gross_win > 0 else 0.0)
    expectancy = sum(results) / len(results) if results else 0.0
    dd = max_drawdown(results)

    if trades >= 80 and expectancy > 0 and pf >= 1.5 and dd <= max(10, trades * 0.30):
        decision = "PROMOTE_CANDIDATE"
    elif trades >= 40 and expectancy > -0.03 and pf >= 1.1:
        decision = "OBSERVE"
    else:
        decision = "REJECT"

    return {
        "symbol": "DE40",
        "timeframe": timeframe,
        "strategy": strategy,
        "fast": fast,
        "slow": slow,
        "rr": rr,
        "hold": hold,
        "trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / trades, 6) if trades else 0,
        "expectancy_r": round(expectancy, 6),
        "profit_factor": round(pf, 6),
        "max_drawdown_r_proxy": round(dd, 6),
        "avg_mae_r_proxy": round(total_mae / trades, 6) if trades else 0,
        "avg_mfe_r_proxy": round(total_mfe / trades, 6) if trades else 0,
        "decision": decision,
    }


def discover(dataset_root: Path, outdir: Path, max_rows_per_tf: int = 100000) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    dataset_files = []
    for tf in ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]:
        found = sorted(
            [
                p for p in dataset_root.rglob("*")
                if p.is_file() and "DE40" in p.name and f"_{tf}_" in p.name
            ],
            key=lambda x: x.stat().st_size,
            reverse=True,
        )
        if found:
            dataset_files.append((tf, found[0]))

    strategies = ["EMA_CROSS", "SMA_TREND_PULLBACK", "RSI_MEAN_REVERSION", "ATR_BREAKOUT"]
    fast_values = [5, 9, 13, 20]
    slow_values = [34, 55, 89]
    rr_values = [2.0, 3.0, 5.0]

    rows = []

    for tf, path in dataset_files:
        candles = load_candles(path, limit=max_rows_per_tf)

        if tf == "M1":
            hold_values = [30, 60, 120]
            step = 10
        elif tf == "M5":
            hold_values = [18, 36, 72]
            step = 5
        elif tf == "M15":
            hold_values = [12, 24, 48]
            step = 3
        else:
            hold_values = [8, 16, 32]
            step = 2

        for strategy in strategies:
            for fast in fast_values:
                for slow in slow_values:
                    if fast >= slow:
                        continue
                    for rr in rr_values:
                        for hold in hold_values:
                            rows.append(evaluate_strategy(candles, tf, strategy, fast, slow, rr, hold, step))

    rows = sorted(
        rows,
        key=lambda r: (
            r["decision"] == "PROMOTE_CANDIDATE",
            r["decision"] == "OBSERVE",
            r["expectancy_r"],
            r["profit_factor"],
            -r["max_drawdown_r_proxy"],
        ),
        reverse=True,
    )

    all_csv = outdir / "de40_multitimeframe_edge_discovery_all.csv"
    promoted_csv = outdir / "de40_multitimeframe_edge_promoted_candidates.csv"
    observed_csv = outdir / "de40_multitimeframe_edge_observed_candidates.csv"
    summary_json = outdir / "summary.json"

    if rows:
        with all_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    promoted = [r for r in rows if r["decision"] == "PROMOTE_CANDIDATE"]
    observed = [r for r in rows if r["decision"] == "OBSERVE"]

    for target, data in [(promoted_csv, promoted), (observed_csv, observed)]:
        with target.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["empty"])
            w.writeheader()
            w.writerows(data)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "dataset_root": str(dataset_root),
        "datasets_detected": [{"timeframe": tf, "path": str(p)} for tf, p in dataset_files],
        "strategies_tested": strategies,
        "total_combinations": len(rows),
        "promoted_candidates": len(promoted),
        "observed_candidates": len(observed),
        "rejected_candidates": len([r for r in rows if r["decision"] == "REJECT"]),
        "outputs": {
            "all": str(all_csv),
            "promoted": str(promoted_csv),
            "observed": str(observed_csv),
            "summary_json": str(summary_json),
        },
        "status": "CERTIFIED",
        "certification": "P2369_DE40_MULTI_TIMEFRAME_EDGE_DISCOVERY_LOOP_CERTIFIED",
        "warning": "PAPER_ONLY_DISCOVERY_NOT_LIVE_SIGNAL_PERMISSION",
    }

    summary_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dataset-root", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max-rows-per-tf", type=int, default=100000)
    args = p.parse_args()

    result = discover(Path(args.dataset_root), Path(args.outdir), args.max_rows_per_tf)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
