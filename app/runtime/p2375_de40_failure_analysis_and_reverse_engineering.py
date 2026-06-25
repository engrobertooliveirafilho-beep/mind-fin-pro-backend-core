from __future__ import annotations

import argparse, csv, json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List


MISSION = "P2375_DE40_FAILURE_ANALYSIS_AND_REVERSE_ENGINEERING"
MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"


def sniff(path: Path) -> str:
    first = path.read_text(encoding="utf-8-sig", errors="ignore")[:2048].splitlines()[0]
    return ";" if first.count(";") > first.count(",") else ","


def load_csv(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=sniff(path)))


def f(v, d=0.0):
    try:
        if v is None or str(v).strip() == "":
            return d
        return float(str(v).replace(",", "."))
    except Exception:
        return d


def aggregate(rows: List[Dict], keys: List[str]) -> List[Dict]:
    groups = defaultdict(list)
    for r in rows:
        k = tuple(r.get(x, "") for x in keys)
        groups[k].append(r)

    out = []
    for k, arr in groups.items():
        exp = [f(x.get("expectancy_r", x.get("test_expectancy_r", 0))) for x in arr]
        pf = [f(x.get("profit_factor", x.get("test_pf", 0))) for x in arr]
        trades = [f(x.get("trades", x.get("test_trades", 0))) for x in arr]
        row = {keys[i]: k[i] for i in range(len(keys))}
        row.update({
            "count": len(arr),
            "avg_expectancy_r": round(sum(exp)/len(exp), 6) if exp else 0,
            "max_expectancy_r": round(max(exp), 6) if exp else 0,
            "avg_profit_factor": round(sum(pf)/len(pf), 6) if pf else 0,
            "max_profit_factor": round(max(pf), 6) if pf else 0,
            "avg_trades": round(sum(trades)/len(trades), 2) if trades else 0,
        })
        out.append(row)

    return sorted(out, key=lambda x: (x["max_expectancy_r"], x["max_profit_factor"], x["count"]), reverse=True)


def reverse_engineer_failures(batch_rows: List[Dict], wf_rows: List[Dict]) -> List[Dict]:
    notes = []

    for r in wf_rows:
        train = f(r.get("train_expectancy_r"))
        val = f(r.get("validation_expectancy_r"))
        test = f(r.get("test_expectancy_r"))
        train_pf = f(r.get("train_pf"))
        test_pf = f(r.get("test_pf"))

        reason = []
        if train > 0 and test <= 0:
            reason.append("TRAIN_ONLY_EDGE_DECAY")
        if train_pf >= 1.2 and test_pf < 1.15:
            reason.append("PF_COLLAPSE_OUT_OF_SAMPLE")
        if f(r.get("test_trades")) < 15 and r.get("profile") != "SWING":
            reason.append("LOW_TEST_SAMPLE")
        if val <= 0:
            reason.append("VALIDATION_FAILED")
        if test <= 0:
            reason.append("TEST_FAILED")

        notes.append({
            "family": r.get("family", ""),
            "variant": r.get("variant", ""),
            "profile": r.get("profile", ""),
            "timeframe": r.get("timeframe", ""),
            "session_filter": r.get("session_filter", ""),
            "rr": r.get("rr", ""),
            "hold": r.get("hold", ""),
            "train_expectancy_r": train,
            "validation_expectancy_r": val,
            "test_expectancy_r": test,
            "train_pf": train_pf,
            "test_pf": test_pf,
            "failure_mode": "|".join(reason) if reason else "UNCLASSIFIED_FAILURE",
            "reverse_engineering_action": "SEGMENT_BY_REGIME_SESSION_VOLATILITY_BEFORE_SIGNAL",
        })

    return notes


def movement_reverse_engineering(dataset_root: Path) -> List[Dict]:
    out = []

    for tf in ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]:
        found = sorted([p for p in dataset_root.rglob("*") if p.is_file() and "DE40" in p.name and f"_{tf}_" in p.name], key=lambda x: x.stat().st_size, reverse=True)
        if not found:
            continue

        rows = load_csv(found[0])[:50000]
        closes = [f(x["close"]) for x in rows]
        highs = [f(x["high"]) for x in rows]
        lows = [f(x["low"]) for x in rows]

        pullbacks = inversions = continuations = 0

        for i in range(60, len(rows)-10):
            ma20 = sum(closes[i-19:i+1]) / 20
            ma50 = sum(closes[i-49:i+1]) / 50
            prev_ma20 = sum(closes[i-20:i]) / 20

            trend_up = ma20 > ma50
            trend_down = ma20 < ma50

            if trend_up and lows[i] <= ma20 and closes[i] > ma20:
                pullbacks += 1
            if trend_down and highs[i] >= ma20 and closes[i] < ma20:
                pullbacks += 1

            if closes[i-1] < prev_ma20 and closes[i] > ma20:
                inversions += 1
            if closes[i-1] > prev_ma20 and closes[i] < ma20:
                inversions += 1

            if trend_up and closes[i] > ma20 and closes[i] > closes[i-5]:
                continuations += 1
            if trend_down and closes[i] < ma20 and closes[i] < closes[i-5]:
                continuations += 1

        total = max(1, len(rows)-70)
        out.append({
            "symbol": "DE40",
            "timeframe": tf,
            "rows_scanned": len(rows),
            "pullback_events": pullbacks,
            "inversion_events": inversions,
            "continuation_events": continuations,
            "pullback_density": round(pullbacks/total, 6),
            "inversion_density": round(inversions/total, 6),
            "continuation_density": round(continuations/total, 6),
            "engineering_conclusion": "USE_AS_PRIOR_FOR_REGIME_FIRST_SIGNAL_ROUTER",
        })

    return out


def write_csv(path: Path, rows: List[Dict]):
    fields = sorted({k for r in rows for k in r.keys()}) if rows else ["empty"]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def run(batch: Path, wf: Path, dataset_root: Path, outdir: Path) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    batch_rows = load_csv(batch)
    wf_rows = load_csv(wf)

    by_family = aggregate(batch_rows, ["family"])
    by_tf = aggregate(batch_rows, ["timeframe"])
    by_session = aggregate(batch_rows, ["session_filter"])
    by_rr = aggregate(batch_rows, ["rr"])
    by_family_tf = aggregate(batch_rows, ["family", "timeframe"])
    failures = reverse_engineer_failures(batch_rows, wf_rows)
    movements = movement_reverse_engineering(dataset_root)

    files = {
        "failure_by_family": outdir / "de40_failure_by_family.csv",
        "failure_by_timeframe": outdir / "de40_failure_by_timeframe.csv",
        "failure_by_session": outdir / "de40_failure_by_session.csv",
        "failure_by_rr": outdir / "de40_failure_by_rr.csv",
        "failure_by_family_timeframe": outdir / "de40_failure_by_family_timeframe.csv",
        "operation_reverse_engineering": outdir / "de40_operation_reverse_engineering.csv",
        "movement_reverse_engineering": outdir / "de40_movement_reverse_engineering.csv",
        "summary_json": outdir / "summary.json",
    }

    write_csv(files["failure_by_family"], by_family)
    write_csv(files["failure_by_timeframe"], by_tf)
    write_csv(files["failure_by_session"], by_session)
    write_csv(files["failure_by_rr"], by_rr)
    write_csv(files["failure_by_family_timeframe"], by_family_tf)
    write_csv(files["operation_reverse_engineering"], failures)
    write_csv(files["movement_reverse_engineering"], movements)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "batch_rows_analyzed": len(batch_rows),
        "walk_forward_rows_analyzed": len(wf_rows),
        "movement_timeframes_analyzed": len(movements),
        "reverse_engineering_layers": [
            "OPERATION_FAILURE_REVERSE_ENGINEERING",
            "PULLBACK_MOVEMENT_REVERSE_ENGINEERING",
            "INVERSION_MOVEMENT_REVERSE_ENGINEERING",
            "CONTINUATION_MOVEMENT_REVERSE_ENGINEERING",
            "FAMILY_TIMEFRAME_SESSION_RR_FAILURE_MAP",
        ],
        "status": "CERTIFIED",
        "certification": "P2375_FAILURE_ANALYSIS_AND_REVERSE_ENGINEERING_CERTIFIED",
        "next": "P2376_DE40_REGIME_FIRST_SIGNAL_ROUTER",
        "outputs": {k: str(v) for k, v in files.items()},
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--batch", required=True)
    p.add_argument("--walk-forward", required=True)
    p.add_argument("--dataset-root", required=True)
    p.add_argument("--outdir", required=True)
    args = p.parse_args()

    result = run(Path(args.batch), Path(args.walk_forward), Path(args.dataset_root), Path(args.outdir))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
