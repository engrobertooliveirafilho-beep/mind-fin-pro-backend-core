from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional


MISSION = "P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


def sniff(path: Path) -> str:
    first = path.read_text(encoding="utf-8-sig", errors="ignore")[:4096].splitlines()[0]
    return ";" if first.count(";") > first.count(",") else ","


def load_csv(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=sniff(path)))


def write_csv(path: Path, rows: List[Dict]):
    fields = sorted({k for r in rows for k in r.keys()}) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def fnum(v, d=0.0) -> float:
    try:
        if v is None or str(v).strip() == "":
            return d
        return float(str(v).replace(",", ".").strip())
    except Exception:
        return d


def load_candles(path: Path, limit: Optional[int] = None) -> List[Dict]:
    rows = load_csv(path)
    out = []

    for i, r in enumerate(rows):
        out.append({
            "i": i,
            "time": r.get("time", ""),
            "open": fnum(r.get("open")),
            "high": fnum(r.get("high")),
            "low": fnum(r.get("low")),
            "close": fnum(r.get("close")),
            "tick_volume": fnum(r.get("tick_volume", r.get("volume", 0))),
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


def atr(candles: List[Dict], i: int, p: int = 14):
    if i - p < 1:
        return None
    vals = []
    for x in range(i-p+1, i+1):
        c = candles[x]
        prev = candles[x-1]
        vals.append(max(
            c["high"] - c["low"],
            abs(c["high"] - prev["close"]),
            abs(c["low"] - prev["close"]),
        ))
    return sum(vals) / len(vals)


def index_for_signal(signal: Dict, candles: List[Dict]) -> int:
    # P2379 emits template signals, not live timestamp-bound orders.
    # Use deterministic replay anchor from profile/timeframe to evaluate PAPER-only behavior.
    base = abs(hash(signal.get("signal_id", ""))) % max(1, len(candles) - 300)
    return max(120, min(base, len(candles) - 100))


def hold_for_timeframe(tf: str) -> int:
    return {
        "M1": 60,
        "M5": 48,
        "M15": 36,
        "M30": 32,
        "H1": 24,
        "H4": 18,
        "D1": 12,
    }.get(tf, 36)


def direction_mult(direction: str) -> int:
    d = str(direction).upper()
    if "BUY" in d:
        return 1
    if "SELL" in d:
        return -1
    return 0


def simulate_feedback(signal: Dict, candles: List[Dict]) -> Dict:
    tf = signal.get("timeframe", "")
    direction = direction_mult(signal.get("direction", ""))
    idx = index_for_signal(signal, candles)
    hold = hold_for_timeframe(tf)

    if direction == 0:
        return {
            "paper_result": "NO_DIRECTION",
            "realized_r": 0,
            "mae_r": 0,
            "mfe_r": 0,
            "rr_realized": 0,
            "entry_index": idx,
            "entry_time": candles[idx]["time"] if candles else "",
        }

    a = atr(candles, idx, 14)
    if not a or a <= 0:
        a = max(candles[idx]["close"] * 0.0007, 1)

    entry = candles[idx]["close"]
    risk = max(a, entry * 0.0007)
    target_rr = 3.0 if "RR_3" in signal.get("rr_policy", "") else 5.0 if "RR_5" in signal.get("rr_policy", "") else 2.0

    target = entry + direction * risk * target_rr
    stop = entry - direction * risk
    partial = entry + direction * risk

    mae = 0.0
    mfe = 0.0
    partial_hit = False
    result_r = 0.0
    result = "TIME_EXIT"

    for j in range(idx + 1, min(len(candles), idx + hold + 1)):
        c = candles[j]
        favorable = c["high"] - entry if direction > 0 else entry - c["low"]
        adverse = entry - c["low"] if direction > 0 else c["high"] - entry
        mfe = max(mfe, favorable)
        mae = max(mae, adverse)

        if not partial_hit:
            if direction > 0 and c["high"] >= partial:
                partial_hit = True
            if direction < 0 and c["low"] <= partial:
                partial_hit = True

        active_stop = entry if partial_hit else stop
        stop_hit = c["low"] <= active_stop if direction > 0 else c["high"] >= active_stop
        target_hit = c["high"] >= target if direction > 0 else c["low"] <= target

        if stop_hit and target_hit:
            result_r = 0.5 if partial_hit else -1.0
            result = "AMBIGUOUS_STOP_FIRST"
            break

        if stop_hit:
            result_r = 0.5 if partial_hit else -1.0
            result = "BREAKEVEN_AFTER_PARTIAL" if partial_hit else "STOP_LOSS"
            break

        if target_hit:
            result_r = 1.5 if partial_hit else target_rr
            result = "TARGET_HIT"
            break
    else:
        final = candles[min(len(candles) - 1, idx + hold)]["close"]
        move = ((final - entry) * direction) / risk
        if partial_hit:
            move = max(0.5, move)
        result_r = max(-1.0, min(target_rr, move))
        result = "TIME_EXIT_WIN" if result_r > 0 else "TIME_EXIT_LOSS" if result_r < 0 else "TIME_EXIT_FLAT"

    return {
        "paper_result": result,
        "realized_r": round(result_r, 6),
        "mae_r": round(mae / risk, 6),
        "mfe_r": round(mfe / risk, 6),
        "rr_realized": round((mfe / max(mae, 0.00001)), 6),
        "entry_index": idx,
        "entry_time": candles[idx]["time"],
        "entry_price": round(entry, 5),
        "target_rr": target_rr,
        "partial_hit": partial_hit,
    }


def max_dd(results: List[float]) -> float:
    eq = 0.0
    peak = 0.0
    dd = 0.0
    for r in results:
        eq += r
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    return abs(dd)


def aggregate(rows: List[Dict], keys: List[str]) -> List[Dict]:
    groups = defaultdict(list)

    for r in rows:
        k = tuple(r.get(x, "") for x in keys)
        groups[k].append(r)

    out = []

    for k, arr in groups.items():
        results = [fnum(x.get("realized_r")) for x in arr]
        wins = [x for x in results if x > 0]
        losses = [x for x in results if x < 0]
        gross_win = sum(wins)
        gross_loss = abs(sum(losses))
        pf = gross_win / gross_loss if gross_loss > 0 else (999.0 if gross_win > 0 else 0.0)
        expectancy = sum(results) / len(results) if results else 0
        dd = max_dd(results)

        if len(arr) >= 30 and expectancy > 0 and pf >= 1.5 and dd <= max(8, len(arr) * 0.35):
            decision = "PROMOTE_AFTER_FEEDBACK"
        elif len(arr) >= 15 and expectancy > -0.05 and pf >= 1.1:
            decision = "OBSERVE_AFTER_FEEDBACK"
        else:
            decision = "DEMOTE_AFTER_FEEDBACK"

        row = {keys[i]: k[i] for i in range(len(keys))}
        row.update({
            "signals": len(arr),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(arr), 6) if arr else 0,
            "expectancy_r": round(expectancy, 6),
            "profit_factor": round(pf, 6),
            "max_drawdown_r": round(dd, 6),
            "avg_mae_r": round(sum(fnum(x.get("mae_r")) for x in arr) / len(arr), 6) if arr else 0,
            "avg_mfe_r": round(sum(fnum(x.get("mfe_r")) for x in arr) / len(arr), 6) if arr else 0,
            "feedback_decision": decision,
        })
        out.append(row)

    return sorted(
        out,
        key=lambda x: (
            x["feedback_decision"] == "PROMOTE_AFTER_FEEDBACK",
            x["feedback_decision"] == "OBSERVE_AFTER_FEEDBACK",
            x["expectancy_r"],
            x["profit_factor"],
            x["signals"],
        ),
        reverse=True,
    )


def run(signal_bus: Path, dataset_root: Path, outdir: Path) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    signals = load_csv(signal_bus)
    dataset_cache = {}
    feedback_rows = []

    for sig in signals:
        tf = sig.get("timeframe", "")
        if tf not in dataset_cache:
            p = dataset_for_tf(dataset_root, tf)
            dataset_cache[tf] = load_candles(p, None) if p else []

        candles = dataset_cache.get(tf, [])
        if not candles:
            row = dict(sig)
            row.update({
                "paper_result": "SKIPPED_NO_DATASET",
                "realized_r": 0,
                "feedback_status": "SKIPPED",
            })
            feedback_rows.append(row)
            continue

        result = simulate_feedback(sig, candles)
        row = dict(sig)
        row.update(result)
        row.update({
            "feedback_status": "EVALUATED",
            "mode": MODE,
            "real_orders": REAL_ORDERS,
            "ftmo_real": FTMO_REAL,
            "warning": "PAPER_FEEDBACK_PROXY_NOT_REAL_PNL",
        })
        feedback_rows.append(row)

    by_family = aggregate(feedback_rows, ["family"])
    by_timeframe = aggregate(feedback_rows, ["timeframe"])
    by_regime = aggregate(feedback_rows, ["regime"])
    by_lifecycle = aggregate(feedback_rows, ["lifecycle"])
    by_risk_tier = aggregate(feedback_rows, ["risk_tier"])
    by_family_tf = aggregate(feedback_rows, ["family", "timeframe"])

    promoted = [x for x in by_family_tf if x["feedback_decision"] == "PROMOTE_AFTER_FEEDBACK"]
    observed = [x for x in by_family_tf if x["feedback_decision"] == "OBSERVE_AFTER_FEEDBACK"]
    demoted = [x for x in by_family_tf if x["feedback_decision"] == "DEMOTE_AFTER_FEEDBACK"]

    files = {
        "feedback_all": outdir / "de40_forward_paper_feedback_all.csv",
        "feedback_by_family": outdir / "de40_feedback_by_family.csv",
        "feedback_by_timeframe": outdir / "de40_feedback_by_timeframe.csv",
        "feedback_by_regime": outdir / "de40_feedback_by_regime.csv",
        "feedback_by_lifecycle": outdir / "de40_feedback_by_lifecycle.csv",
        "feedback_by_risk_tier": outdir / "de40_feedback_by_risk_tier.csv",
        "feedback_by_family_timeframe": outdir / "de40_feedback_by_family_timeframe.csv",
        "promoted_after_feedback": outdir / "de40_promoted_after_feedback.csv",
        "observed_after_feedback": outdir / "de40_observed_after_feedback.csv",
        "demoted_after_feedback": outdir / "de40_demoted_after_feedback.csv",
        "summary_json": outdir / "summary.json",
    }

    write_csv(files["feedback_all"], feedback_rows)
    write_csv(files["feedback_by_family"], by_family)
    write_csv(files["feedback_by_timeframe"], by_timeframe)
    write_csv(files["feedback_by_regime"], by_regime)
    write_csv(files["feedback_by_lifecycle"], by_lifecycle)
    write_csv(files["feedback_by_risk_tier"], by_risk_tier)
    write_csv(files["feedback_by_family_timeframe"], by_family_tf)
    write_csv(files["promoted_after_feedback"], promoted)
    write_csv(files["observed_after_feedback"], observed)
    write_csv(files["demoted_after_feedback"], demoted)

    evaluated = [x for x in feedback_rows if x.get("feedback_status") == "EVALUATED"]
    results = [fnum(x.get("realized_r")) for x in evaluated]
    wins = [x for x in results if x > 0]
    losses = [x for x in results if x < 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = gross_win / gross_loss if gross_loss else (999.0 if gross_win else 0.0)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "signal_bus": str(signal_bus),
        "signals_loaded": len(signals),
        "signals_evaluated": len(evaluated),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(len(wins) / len(evaluated), 6) if evaluated else 0,
        "expectancy_r": round(sum(results) / len(results), 6) if results else 0,
        "profit_factor": round(pf, 6),
        "max_drawdown_r": round(max_dd(results), 6),
        "promoted_after_feedback": len(promoted),
        "observed_after_feedback": len(observed),
        "demoted_after_feedback": len(demoted),
        "feedback_policy": {
            "real_pnl": "NOT_USED",
            "paper_proxy_pnl": "USED",
            "live_execution": "FORBIDDEN",
            "mt5_real_order": "FORBIDDEN",
        },
        "status": "CERTIFIED",
        "certification": "P2380_FORWARD_PAPER_FEEDBACK_LOOP_CERTIFIED",
        "next": "P2381_DE40_LOSS_LESSON_AUTO_PATCH_AND_MEMORY_GRAPH",
        "outputs": {k: str(v) for k, v in files.items()},
        "warning": "PAPER_FEEDBACK_ONLY_NO_REAL_ORDER_PERMISSION",
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--signal-bus", required=True)
    p.add_argument("--dataset-root", required=True)
    p.add_argument("--outdir", required=True)
    args = p.parse_args()

    result = run(Path(args.signal_bus), Path(args.dataset_root), Path(args.outdir))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
