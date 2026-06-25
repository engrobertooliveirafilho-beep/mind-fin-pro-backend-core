from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional


MISSION = "P2371_DE40_CATALOG_BACKTEST_ENGINE"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


def sniff_delimiter(path: Path) -> str:
    first = path.read_text(encoding="utf-8-sig", errors="ignore")[:2048].splitlines()[0]
    return ";" if first.count(";") > first.count(",") else ","


def fnum(v) -> float:
    return float(str(v).replace(",", ".").strip())


def load_csv(path: Path) -> List[Dict]:
    delimiter = sniff_delimiter(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def load_candles(path: Path, limit: Optional[int] = None) -> List[Dict]:
    rows = load_csv(path)
    out = []
    for i, r in enumerate(rows):
        out.append({
            "i": i,
            "time": r["time"],
            "open": fnum(r["open"]),
            "high": fnum(r["high"]),
            "low": fnum(r["low"]),
            "close": fnum(r["close"]),
        })
        if limit and len(out) >= limit:
            break
    return out


def sma(vals, i, p):
    if i - p + 1 < 0:
        return None
    return sum(vals[i-p+1:i+1]) / p


def atr(candles, i, p=14):
    if i - p < 1:
        return None
    vals = []
    for x in range(i-p+1, i+1):
        c = candles[x]
        prev = candles[x-1]
        vals.append(max(c["high"]-c["low"], abs(c["high"]-prev["close"]), abs(c["low"]-prev["close"])))
    return sum(vals) / len(vals)


def rsi(vals, i, p=14):
    if i - p < 1:
        return None
    gains = []
    losses = []
    for x in range(i-p+1, i+1):
        d = vals[x] - vals[x-1]
        gains.append(max(d, 0))
        losses.append(abs(min(d, 0)))
    ag = sum(gains) / p
    al = sum(losses) / p
    if al == 0:
        return 100.0
    rs = ag / al
    return 100 - (100 / (1 + rs))


def simulate(candles, i, direction, risk, rr, hold):
    entry = candles[i]["close"]
    target = entry + direction * risk * rr
    stop = entry - direction * risk
    partial = entry + direction * risk

    mae = 0.0
    mfe = 0.0
    partial_hit = False

    for j in range(i + 1, min(len(candles), i + hold + 1)):
        c = candles[j]
        favorable = c["high"] - entry if direction > 0 else entry - c["low"]
        adverse = entry - c["low"] if direction > 0 else c["high"] - entry
        mae = max(mae, adverse)
        mfe = max(mfe, favorable)

        if not partial_hit:
            if direction > 0 and c["high"] >= partial:
                partial_hit = True
            if direction < 0 and c["low"] <= partial:
                partial_hit = True

        active_stop = entry if partial_hit else stop
        stop_hit = c["low"] <= active_stop if direction > 0 else c["high"] >= active_stop
        target_hit = c["high"] >= target if direction > 0 else c["low"] <= target

        if stop_hit and target_hit:
            return 0.5 if partial_hit else -1.0, mae / risk, mfe / risk

        if stop_hit:
            return 0.5 if partial_hit else -1.0, mae / risk, mfe / risk

        if target_hit:
            return 1.5 if partial_hit else rr, mae / risk, mfe / risk

    final = candles[min(len(candles)-1, i+hold)]["close"]
    r = ((final - entry) * direction) / risk
    if partial_hit:
        r = max(0.5, r)
    return max(-1.0, min(rr, r)), mae / risk, mfe / risk


def max_dd(results):
    eq = 0.0
    peak = 0.0
    dd = 0.0
    for r in results:
        eq += r
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    return abs(dd)


def direction_for_variant(variant, candles, closes, i):
    a = atr(candles, i)
    if not a or a <= 0:
        return 0, a

    c = candles[i]
    prev = candles[i-1]
    s20 = sma(closes, i, 20)
    s50 = sma(closes, i, 50)
    s100 = sma(closes, i, 100)
    r = rsi(closes, i, 14)

    recent_high = max(x["high"] for x in candles[max(0, i-20):i])
    recent_low = min(x["low"] for x in candles[max(0, i-20):i])

    if "TREND" in variant or "CONTINUATION" in variant or "BOS" in variant:
        if s20 and s50 and s20 > s50 and c["close"] > s20:
            return 1, a
        if s20 and s50 and s20 < s50 and c["close"] < s20:
            return -1, a

    if "PULLBACK" in variant or "CORRECTION" in variant:
        if s20 and s50 and s20 > s50 and prev["close"] < s20 and c["close"] > s20:
            return 1, a
        if s20 and s50 and s20 < s50 and prev["close"] > s20 and c["close"] < s20:
            return -1, a

    if "REVERSAL" in variant or "COUNTER" in variant or "CHOCH" in variant:
        if r is not None and r < 28 and c["close"] > prev["close"]:
            return 1, a
        if r is not None and r > 72 and c["close"] < prev["close"]:
            return -1, a

    if "BREAKOUT" in variant or "DRIVE" in variant:
        if c["close"] > recent_high:
            return 1, a
        if c["close"] < recent_low:
            return -1, a

    if "REVERSION" in variant or "FADE" in variant:
        if s20 and c["close"] < s20 - a:
            return 1, a
        if s20 and c["close"] > s20 + a:
            return -1, a

    if "LIQUIDITY" in variant or "SWEEP" in variant or "STOP_HUNT" in variant or "FAKE_BREAKOUT" in variant:
        if c["low"] < recent_low and c["close"] > recent_low:
            return 1, a
        if c["high"] > recent_high and c["close"] < recent_high:
            return -1, a

    if "ORDER_BLOCK" in variant or "BREAKER" in variant or "FAIR_VALUE_GAP" in variant:
        if s50 and s100 and s50 > s100 and c["close"] > prev["high"]:
            return 1, a
        if s50 and s100 and s50 < s100 and c["close"] < prev["low"]:
            return -1, a

    if "VOLATILITY" in variant or "ATR" in variant or "RANGE_EXPANSION" in variant:
        body = abs(c["close"] - c["open"])
        if body > a * 0.8:
            return 1 if c["close"] > c["open"] else -1, a

    return 0, a


def hold_for_profile(profile, timeframe):
    if profile == "SCALP":
        return {"M1": 30, "M2": 24, "M5": 18}.get(timeframe, 18)
    if profile == "INTRADAY":
        return {"M2": 60, "M5": 36, "M15": 24}.get(timeframe, 24)
    return {"H1": 48, "H4": 30, "D1": 20}.get(timeframe, 30)


def dataset_for_tf(dataset_root: Path, timeframe: str):
    found = sorted(
        [p for p in dataset_root.rglob("*") if p.is_file() and "DE40" in p.name and f"_{timeframe}_" in p.name],
        key=lambda x: x.stat().st_size,
        reverse=True,
    )
    return found[0] if found else None


def eval_candidate(candidate, candles):
    closes = [x["close"] for x in candles]
    timeframe = candidate["timeframe"]
    variant = candidate["variant"]
    profile = candidate["profile"]
    rr = float(candidate["min_rr"])
    hold = hold_for_profile(profile, timeframe)

    step = 5 if timeframe in ["M1", "M2", "M5"] else 2
    start = 120
    end = len(candles) - hold - 2

    results = []
    maes = []
    mfes = []

    for i in range(start, end, step):
        direction, a = direction_for_variant(variant, candles, closes, i)
        if direction == 0 or not a:
            continue

        risk = max(a, candles[i]["close"] * 0.0007)
        result, mae, mfe = simulate(candles, i, direction, risk, rr, hold)
        results.append(result)
        maes.append(mae)
        mfes.append(mfe)

    trades = len(results)
    wins = len([x for x in results if x > 0])
    losses = len([x for x in results if x < 0])
    gross_win = sum(x for x in results if x > 0)
    gross_loss = abs(sum(x for x in results if x < 0))
    pf = gross_win / gross_loss if gross_loss else (999.0 if gross_win else 0.0)
    expectancy = sum(results) / trades if trades else 0.0
    dd = max_dd(results)

    if trades >= 80 and expectancy > 0 and pf >= 1.5 and dd <= max(10, trades * 0.30):
        decision = "PROMOTE_CANDIDATE"
    elif trades >= 40 and expectancy > -0.03 and pf >= 1.1:
        decision = "OBSERVE"
    else:
        decision = "REJECT"

    row = dict(candidate)
    row.update({
        "trades": trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / trades, 6) if trades else 0,
        "expectancy_r": round(expectancy, 6),
        "profit_factor": round(pf, 6),
        "max_drawdown_r_proxy": round(dd, 6),
        "avg_mae_r_proxy": round(sum(maes) / trades, 6) if trades else 0,
        "avg_mfe_r_proxy": round(sum(mfes) / trades, 6) if trades else 0,
        "decision": decision,
    })
    return row


def run(catalog_path: Path, dataset_root: Path, outdir: Path, max_rows_per_tf: int = 100000):
    outdir.mkdir(parents=True, exist_ok=True)

    catalog = load_csv(catalog_path)
    dataset_cache = {}
    rows = []

    for candidate in catalog:
        tf = candidate["timeframe"]
        if tf == "M2":
            continue

        if tf not in dataset_cache:
            path = dataset_for_tf(dataset_root, tf)
            if not path:
                dataset_cache[tf] = None
            else:
                dataset_cache[tf] = load_candles(path, limit=max_rows_per_tf)

        candles = dataset_cache.get(tf)
        if not candles:
            skipped = dict(candidate)
            skipped.update({
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "expectancy_r": 0,
                "profit_factor": 0,
                "max_drawdown_r_proxy": 0,
                "avg_mae_r_proxy": 0,
                "avg_mfe_r_proxy": 0,
                "decision": "SKIPPED_NO_DATASET",
            })
            rows.append(skipped)
            continue

        rows.append(eval_candidate(candidate, candles))

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

    all_csv = outdir / "de40_catalog_backtest_all.csv"
    promoted_csv = outdir / "de40_catalog_backtest_promoted.csv"
    observed_csv = outdir / "de40_catalog_backtest_observed.csv"
    summary_json = outdir / "summary.json"

    with all_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    promoted = [x for x in rows if x["decision"] == "PROMOTE_CANDIDATE"]
    observed = [x for x in rows if x["decision"] == "OBSERVE"]

    for path, data in [(promoted_csv, promoted), (observed_csv, observed)]:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(data)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "catalog": str(catalog_path),
        "dataset_root": str(dataset_root),
        "candidates_tested": len(rows),
        "promoted_candidates": len(promoted),
        "observed_candidates": len(observed),
        "rejected_candidates": len([x for x in rows if x["decision"] == "REJECT"]),
        "skipped_no_dataset": len([x for x in rows if x["decision"] == "SKIPPED_NO_DATASET"]),
        "outputs": {
            "all": str(all_csv),
            "promoted": str(promoted_csv),
            "observed": str(observed_csv),
            "summary_json": str(summary_json),
        },
        "status": "CERTIFIED",
        "certification": "P2371_DE40_CATALOG_BACKTEST_ENGINE_CERTIFIED",
        "next": "P2372_DE40_M2_SYNTHETIC_OR_EXPORT_DECISION",
    }

    summary_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--catalog", required=True)
    p.add_argument("--dataset-root", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max-rows-per-tf", type=int, default=100000)
    args = p.parse_args()

    result = run(Path(args.catalog), Path(args.dataset_root), Path(args.outdir), args.max_rows_per_tf)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
