from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional


MISSION = "P2374_DE40_OBSERVED_CANDIDATE_DEEP_WALK_FORWARD"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


def sniff_delimiter(path: Path) -> str:
    first = path.read_text(encoding="utf-8-sig", errors="ignore")[:4096].splitlines()[0]
    return ";" if first.count(";") > first.count(",") else ","


def load_csv(path: Path) -> List[Dict]:
    delimiter = sniff_delimiter(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def fnum(v, default=0.0) -> float:
    try:
        if v is None or str(v).strip() == "":
            return default
        return float(str(v).replace(",", ".").strip())
    except Exception:
        return default


def inum(v, default=0) -> int:
    try:
        if v is None or str(v).strip() == "":
            return default
        return int(float(str(v).replace(",", ".").strip()))
    except Exception:
        return default


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


def dataset_for_tf(dataset_root: Path, timeframe: str):
    found = sorted(
        [p for p in dataset_root.rglob("*") if p.is_file() and "DE40" in p.name and f"_{timeframe}_" in p.name],
        key=lambda x: x.stat().st_size,
        reverse=True,
    )
    return found[0] if found else None


def sma(vals, i, p):
    if p <= 0 or i - p + 1 < 0:
        return None
    return sum(vals[i-p+1:i+1]) / p


def atr(candles, i, p=14):
    if i - p < 1:
        return None
    vals = []
    for x in range(i-p+1, i+1):
        c = candles[x]
        prev = candles[x-1]
        vals.append(max(c["high"] - c["low"], abs(c["high"] - prev["close"]), abs(c["low"] - prev["close"])))
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


def session_of(time_text: str) -> str:
    try:
        hour = int(str(time_text).replace("T", " ").split(" ")[1].split(":")[0])
    except Exception:
        return "UNKNOWN"
    if 7 <= hour < 11:
        return "EUROPE_OPEN"
    if 11 <= hour < 15:
        return "EUROPE_MID"
    if 15 <= hour < 18:
        return "US_OVERLAP"
    return "OFF_SESSION"


def session_allowed(candidate: Dict, time_text: str) -> bool:
    filt = str(candidate.get("session_filter", "ALL_ACTIVE"))
    if filt in ["ALL", ""]:
        return True
    if filt == "ALL_ACTIVE":
        return session_of(time_text) != "OFF_SESSION"
    return session_of(time_text) == filt


def max_dd(results: List[float]) -> float:
    eq = 0.0
    peak = 0.0
    dd = 0.0
    for r in results:
        eq += r
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    return abs(dd)


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


def direction_for_candidate(candidate, candles, closes, i):
    family = candidate.get("family", "")
    a = atr(candles, i, 14)
    if not a or a <= 0:
        return 0, a

    c = candles[i]
    prev = candles[i-1]
    fast = inum(candidate.get("fast"), 20)
    slow = inum(candidate.get("slow"), 50)
    lookback = max(5, inum(candidate.get("lookback"), inum(candidate.get("structure_lookback"), inum(candidate.get("sweep_lookback"), 20))))

    s_fast = sma(closes, i, fast)
    s_slow = sma(closes, i, slow)
    s20 = sma(closes, i, 20)
    s50 = sma(closes, i, 50)
    r = rsi(closes, i, 14)

    recent = candles[max(0, i-lookback):i]
    if not recent:
        return 0, a

    recent_high = max(x["high"] for x in recent)
    recent_low = min(x["low"] for x in recent)
    buffer = fnum(candidate.get("entry_buffer"), fnum(candidate.get("breakout_buffer"), 0.0)) * a

    if family == "TREND_FOLLOWING":
        if s_fast and s_slow and s_fast > s_slow and c["close"] > s_fast + buffer:
            return 1, a
        if s_fast and s_slow and s_fast < s_slow and c["close"] < s_fast - buffer:
            return -1, a

    if family == "PULLBACK":
        depth = fnum(candidate.get("pullback_depth"), 0.5)
        if s_fast and s_slow and s_fast > s_slow and prev["low"] <= s_fast - a * depth and c["close"] > s_fast:
            return 1, a
        if s_fast and s_slow and s_fast < s_slow and prev["high"] >= s_fast + a * depth and c["close"] < s_fast:
            return -1, a

    if family == "REVERSAL":
        threshold = fnum(candidate.get("rsi_threshold"), 30)
        strength = fnum(candidate.get("reversal_strength"), 1.0)
        if r is not None and threshold <= 50 and r <= threshold and (c["close"] - c["open"]) > a * 0.1 * strength:
            return 1, a
        if r is not None and threshold > 50 and r >= threshold and (c["open"] - c["close"]) > a * 0.1 * strength:
            return -1, a

    if family == "COUNTER_TREND":
        ext = fnum(candidate.get("extension_atr"), 1.5)
        if s20 and r is not None and r < 35 and c["close"] < s20 - a * ext:
            return 1, a
        if s20 and r is not None and r > 65 and c["close"] > s20 + a * ext:
            return -1, a

    if family == "BREAKOUT":
        if c["close"] > recent_high + buffer:
            return 1, a
        if c["close"] < recent_low - buffer:
            return -1, a

    if family == "MEAN_REVERSION":
        window = max(10, inum(candidate.get("mean_window"), 20))
        mean = sma(closes, i, window)
        z = fnum(candidate.get("zscore_threshold"), 1.5)
        if mean and c["close"] < mean - a * z:
            return 1, a
        if mean and c["close"] > mean + a * z:
            return -1, a

    if family == "LIQUIDITY":
        depth = fnum(candidate.get("sweep_depth_atr"), 0.25)
        if c["low"] < recent_low - a * depth and c["close"] > recent_low:
            return 1, a
        if c["high"] > recent_high + a * depth and c["close"] < recent_high:
            return -1, a

    if family == "SMART_MONEY":
        if s20 and s50 and s20 > s50 and c["close"] > prev["high"]:
            return 1, a
        if s20 and s50 and s20 < s50 and c["close"] < prev["low"]:
            return -1, a

    if family == "SESSION":
        mode = candidate.get("session_mode", "")
        if mode == "OPEN_DRIVE":
            if c["close"] > recent_high + buffer:
                return 1, a
            if c["close"] < recent_low - buffer:
                return -1, a
        if mode in ["REVERSAL", "FADE"]:
            if c["high"] > recent_high and c["close"] < recent_high:
                return -1, a
            if c["low"] < recent_low and c["close"] > recent_low:
                return 1, a

    if family == "VOLATILITY":
        body = abs(c["close"] - c["open"])
        threshold = fnum(candidate.get("expansion_threshold"), 1.0)
        if body > a * threshold:
            return 1 if c["close"] > c["open"] else -1, a

    return 0, a


def evaluate_segment(candidate: Dict, candles: List[Dict], start_frac: float, end_frac: float) -> Dict:
    closes = [x["close"] for x in candles]
    rr = fnum(candidate.get("rr"), fnum(candidate.get("min_rr"), 2.0))
    hold = max(3, inum(candidate.get("hold"), 24))
    atr_mult = max(0.2, fnum(candidate.get("atr_multiplier"), 1.0))
    step = 10 if candidate.get("timeframe") == "M1" else 5 if candidate.get("timeframe") in ["M5", "M15"] else 2

    start = max(120, int(len(candles) * start_frac))
    end = min(len(candles) - hold - 2, int(len(candles) * end_frac))

    results = []
    maes = []
    mfes = []

    for i in range(start, end, step):
        if not session_allowed(candidate, candles[i]["time"]):
            continue
        direction, a = direction_for_candidate(candidate, candles, closes, i)
        if direction == 0 or not a:
            continue
        risk = max(a * atr_mult, candles[i]["close"] * 0.0007)
        r, mae, mfe = simulate(candles, i, direction, risk, rr, hold)
        results.append(r)
        maes.append(mae)
        mfes.append(mfe)

    trades = len(results)
    wins = len([x for x in results if x > 0])
    gross_win = sum(x for x in results if x > 0)
    gross_loss = abs(sum(x for x in results if x < 0))
    pf = gross_win / gross_loss if gross_loss else (999.0 if gross_win else 0.0)

    return {
        "trades": trades,
        "wins": wins,
        "win_rate": round(wins / trades, 6) if trades else 0,
        "expectancy_r": round(sum(results) / trades, 6) if trades else 0,
        "profit_factor": round(pf, 6),
        "max_drawdown_r_proxy": round(max_dd(results), 6),
        "avg_mae_r_proxy": round(sum(maes) / trades, 6) if trades else 0,
        "avg_mfe_r_proxy": round(sum(mfes) / trades, 6) if trades else 0,
    }


def walk_forward(candidate: Dict, candles: List[Dict]) -> Dict:
    train = evaluate_segment(candidate, candles, 0.00, 0.60)
    validation = evaluate_segment(candidate, candles, 0.60, 0.80)
    test = evaluate_segment(candidate, candles, 0.80, 1.00)

    min_train = 40 if candidate.get("profile") != "SWING" else 10
    min_val = 15 if candidate.get("profile") != "SWING" else 5
    min_test = 15 if candidate.get("profile") != "SWING" else 5

    stable = (
        train["trades"] >= min_train and
        validation["trades"] >= min_val and
        test["trades"] >= min_test and
        train["expectancy_r"] > 0 and
        validation["expectancy_r"] > 0 and
        test["expectancy_r"] > 0 and
        train["profit_factor"] >= 1.2 and
        validation["profit_factor"] >= 1.15 and
        test["profit_factor"] >= 1.15
    )

    if stable and test["profit_factor"] >= 1.5:
        decision = "PROMOTE_WALK_FORWARD"
    elif stable:
        decision = "OBSERVE_WALK_FORWARD"
    else:
        decision = "REJECT_WALK_FORWARD"

    row = dict(candidate)
    row.update({
        "train_trades": train["trades"],
        "train_expectancy_r": train["expectancy_r"],
        "train_pf": train["profit_factor"],
        "validation_trades": validation["trades"],
        "validation_expectancy_r": validation["expectancy_r"],
        "validation_pf": validation["profit_factor"],
        "test_trades": test["trades"],
        "test_expectancy_r": test["expectancy_r"],
        "test_pf": test["profit_factor"],
        "test_max_drawdown_r_proxy": test["max_drawdown_r_proxy"],
        "test_avg_mae_r_proxy": test["avg_mae_r_proxy"],
        "test_avg_mfe_r_proxy": test["avg_mfe_r_proxy"],
        "walk_forward_decision": decision,
    })
    return row


def run(observed_path: Path, dataset_root: Path, outdir: Path, max_rows_per_tf: int = 100000):
    outdir.mkdir(parents=True, exist_ok=True)

    observed = load_csv(observed_path)
    dataset_cache = {}
    rows = []

    for candidate in observed:
        tf = candidate.get("timeframe")
        if tf == "M2":
            continue

        if tf not in dataset_cache:
            path = dataset_for_tf(dataset_root, tf)
            dataset_cache[tf] = load_candles(path, max_rows_per_tf) if path else None

        candles = dataset_cache.get(tf)
        if not candles:
            continue

        rows.append(walk_forward(candidate, candles))

    rows = sorted(
        rows,
        key=lambda r: (
            r["walk_forward_decision"] == "PROMOTE_WALK_FORWARD",
            r["walk_forward_decision"] == "OBSERVE_WALK_FORWARD",
            fnum(r["test_expectancy_r"]),
            fnum(r["test_pf"]),
            -fnum(r["test_max_drawdown_r_proxy"]),
        ),
        reverse=True,
    )

    all_csv = outdir / "de40_observed_walk_forward_all.csv"
    promoted_csv = outdir / "de40_observed_walk_forward_promoted.csv"
    observed_csv = outdir / "de40_observed_walk_forward_observed.csv"
    summary_json = outdir / "summary.json"

    fieldnames = sorted({k for r in rows for k in r.keys()}) if rows else ["empty"]

    with all_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    promoted = [x for x in rows if x["walk_forward_decision"] == "PROMOTE_WALK_FORWARD"]
    observed_wf = [x for x in rows if x["walk_forward_decision"] == "OBSERVE_WALK_FORWARD"]

    for path, data in [(promoted_csv, promoted), (observed_csv, observed_wf)]:
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(data)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "observed_source": str(observed_path),
        "dataset_root": str(dataset_root),
        "input_observed": len(observed),
        "tested_walk_forward": len(rows),
        "promoted_walk_forward": len(promoted),
        "observed_walk_forward": len(observed_wf),
        "rejected_walk_forward": len([x for x in rows if x["walk_forward_decision"] == "REJECT_WALK_FORWARD"]),
        "outputs": {
            "all": str(all_csv),
            "promoted": str(promoted_csv),
            "observed": str(observed_csv),
            "summary_json": str(summary_json),
        },
        "status": "CERTIFIED",
        "certification": "P2374_DE40_OBSERVED_CANDIDATE_DEEP_WALK_FORWARD_CERTIFIED",
        "next": "P2375_DE40_ANTI_OVERFIT_STRESS_TEST",
        "warning": "WALK_FORWARD_PROMOTION_IS_STILL_PAPER_ONLY",
    }

    summary_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--observed", required=True)
    p.add_argument("--dataset-root", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--max-rows-per-tf", type=int, default=100000)
    args = p.parse_args()

    result = run(Path(args.observed), Path(args.dataset_root), Path(args.outdir), args.max_rows_per_tf)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
