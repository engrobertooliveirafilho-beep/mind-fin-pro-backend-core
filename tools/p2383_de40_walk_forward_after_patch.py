import csv, json, math, os, statistics
from datetime import datetime
from pathlib import Path
from collections import defaultdict

REQUIRED_COLUMNS = [
    "entry_time","family","footprint","lifecycle","regime","session","timeframe",
    "realized_r","mae_r","mfe_r","rr_realized","profit_factor_proxy","expectancy_r_proxy"
]

PROMOTE_PF = 1.5
PROMOTE_EXPECTANCY = 0.0
PROMOTE_WR = 45.0
PROMOTE_SAMPLES = 30
PROMOTE_WINDOWS = 4
OBSERVE_WINDOWS = 3
WINDOW_COUNT = 5

MODE = "PAPER_ONLY"
REAL_ORDERS = "FORBIDDEN"
FTMO_REAL = "FORBIDDEN"

def safety_lock():
    assert MODE == "PAPER_ONLY"
    assert REAL_ORDERS == "FORBIDDEN"
    assert FTMO_REAL == "FORBIDDEN"

def fnum(x, default=0.0):
    try:
        if x is None or str(x).strip() == "":
            return default
        return float(str(x).replace(",", "."))
    except Exception:
        return default

def parse_time(x):
    s = str(x).strip()
    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
    ):
        try:
            return datetime.strptime(s[:19], fmt)
        except Exception:
            pass
    return datetime.min

def read_csv_auto(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        delimiter = ";" if sample.count(";") >= sample.count(",") else ","
        return list(csv.DictReader(f, delimiter=delimiter))

def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k:r.get(k,"") for k in fields})

def metrics(rows):
    n = len(rows)
    if n == 0:
        return {
            "samples":0,"wins":0,"losses":0,"winrate":0.0,
            "gross_win":0.0,"gross_loss":0.0,"pf":0.0,
            "expectancy":0.0,"max_dd_r":0.0
        }

    rs = [fnum(r.get("realized_r")) for r in rows]
    wins = [x for x in rs if x > 0]
    losses = [x for x in rs if x < 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = 999.0 if gross_loss == 0 and gross_win > 0 else (gross_win / gross_loss if gross_loss > 0 else 0.0)
    expectancy = sum(rs) / n
    wr = len(wins) / n * 100.0

    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in rs:
        equity += r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)

    return {
        "samples":n,
        "wins":len(wins),
        "losses":len(losses),
        "winrate":round(wr,6),
        "gross_win":round(gross_win,6),
        "gross_loss":round(gross_loss,6),
        "pf":round(pf,6),
        "expectancy":round(expectancy,6),
        "max_dd_r":round(max_dd,6),
    }

def pass_gate(m):
    return (
        m["pf"] >= PROMOTE_PF and
        m["expectancy"] > PROMOTE_EXPECTANCY and
        m["winrate"] >= PROMOTE_WR and
        m["samples"] >= PROMOTE_SAMPLES
    )

def classify(passed_windows):
    if passed_windows >= PROMOTE_WINDOWS:
        return "PROMOTE"
    if passed_windows >= OBSERVE_WINDOWS:
        return "OBSERVE"
    return "REJECT"

def windowize(rows):
    rows = sorted(rows, key=lambda r: parse_time(r.get("entry_time")))
    n = len(rows)
    windows = []
    for i in range(WINDOW_COUNT):
        start = math.floor(i * n / WINDOW_COUNT)
        end = math.floor((i + 1) * n / WINDOW_COUNT)
        part = rows[start:end]
        windows.append({
            "window_id": i + 1,
            "start_index": start,
            "end_index": max(end - 1, start),
            "start_time": part[0].get("entry_time","") if part else "",
            "end_time": part[-1].get("entry_time","") if part else "",
            "samples": len(part),
            "rows": part,
        })
    return windows

def group_key(r):
    return (
        r.get("family","UNKNOWN"),
        r.get("regime","UNKNOWN"),
        r.get("session","UNKNOWN"),
        r.get("footprint","UNKNOWN"),
        r.get("lifecycle","UNKNOWN"),
        r.get("timeframe","UNKNOWN"),
    )

def stability_matrix(rows, dimension):
    out = []
    for val, bucket in sorted(defaultdict(list, { }).items()):
        pass

    d = defaultdict(list)
    for r in rows:
        d[r.get(dimension, "UNKNOWN")].append(r)

    for val, bucket in sorted(d.items(), key=lambda x: str(x[0])):
        m = metrics(bucket)
        out.append({
            dimension: val,
            **m,
            "passed": pass_gate(m),
            "status": "STABLE" if pass_gate(m) else "UNSTABLE"
        })
    return out

def run(prev_dir, out_dir):
    safety_lock()

    prev = Path(prev_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    candidates = [
        prev / "de40_replay_after_patch_all.csv",
        prev / "de40_patched_replay_candidates.csv",
        prev / "de40_walk_forward_input.csv",
    ]
    src = next((p for p in candidates if p.exists()), None)
    if not src:
        csvs = list(prev.glob("*.csv"))
        src = csvs[0] if csvs else None

    if not src:
        raise FileNotFoundError(f"No CSV input found in {prev}")

    rows = read_csv_auto(src)
    if not rows:
        raise ValueError("Input CSV is empty")

    missing = [c for c in REQUIRED_COLUMNS if c not in rows[0]]
    if missing:
        raise ValueError(f"Missing schema columns: {missing}")

    windows = windowize(rows)

    window_rows = []
    for w in windows:
        wm = metrics(w["rows"])
        window_rows.append({
            "window_id": w["window_id"],
            "start_time": w["start_time"],
            "end_time": w["end_time"],
            **wm,
            "passed": pass_gate(wm)
        })

    grouped = defaultdict(lambda: defaultdict(list))
    for w in windows:
        for r in w["rows"]:
            grouped[group_key(r)][w["window_id"]].append(r)

    result_rows = []
    promoted = []
    observed = []
    rejected = []

    for key, by_window in grouped.items():
        family, regime, session, footprint, lifecycle, timeframe = key
        passed = 0
        total_samples = 0
        pfs = []
        exps = []
        wrs = []

        row = {
            "family": family,
            "regime": regime,
            "session": session,
            "footprint": footprint,
            "lifecycle": lifecycle,
            "timeframe": timeframe,
        }

        for i in range(1, WINDOW_COUNT + 1):
            m = metrics(by_window.get(i, []))
            ok = pass_gate(m)
            if ok:
                passed += 1
            total_samples += m["samples"]
            pfs.append(m["pf"])
            exps.append(m["expectancy"])
            wrs.append(m["winrate"])

            row[f"w{i}_samples"] = m["samples"]
            row[f"w{i}_pf"] = m["pf"]
            row[f"w{i}_expectancy"] = m["expectancy"]
            row[f"w{i}_winrate"] = m["winrate"]
            row[f"w{i}_passed"] = ok

        status = classify(passed)
        row["passed_windows"] = passed
        row["total_samples"] = total_samples
        row["avg_pf"] = round(sum(pfs) / len(pfs), 6)
        row["avg_expectancy"] = round(sum(exps) / len(exps), 6)
        row["avg_winrate"] = round(sum(wrs) / len(wrs), 6)
        row["status"] = status

        result_rows.append(row)
        if status == "PROMOTE":
            promoted.append(row)
        elif status == "OBSERVE":
            observed.append(row)
        else:
            rejected.append(row)

    result_fields = list(result_rows[0].keys()) if result_rows else [
        "family","regime","session","footprint","lifecycle","timeframe","status"
    ]

    write_csv(out / "de40_walk_forward_windows.csv", window_rows, list(window_rows[0].keys()))
    write_csv(out / "de40_walk_forward_results.csv", result_rows, result_fields)
    write_csv(out / "de40_walk_forward_promoted.csv", promoted, result_fields)
    write_csv(out / "de40_walk_forward_observed.csv", observed, result_fields)
    write_csv(out / "de40_walk_forward_rejected.csv", rejected, result_fields)

    for dim, fname in [
        ("regime", "de40_regime_stability_matrix.csv"),
        ("session", "de40_session_stability_matrix.csv"),
        ("family", "de40_family_stability_matrix.csv"),
        ("footprint", "de40_footprint_stability_matrix.csv"),
        ("lifecycle", "de40_lifecycle_stability_matrix.csv"),
    ]:
        sm = stability_matrix(rows, dim)
        write_csv(out / fname, sm, list(sm[0].keys()) if sm else [dim])

    all_metrics = metrics(rows)
    summary = {
        "mission": "P2383_DE40_WALK_FORWARD_AFTER_PATCH",
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "input": str(src),
        "output": str(out),
        "schema_confirmed": REQUIRED_COLUMNS,
        "windows": WINDOW_COUNT,
        "criteria": {
            "PROMOTE": {
                "pf_gte": PROMOTE_PF,
                "expectancy_gt": PROMOTE_EXPECTANCY,
                "winrate_gte": PROMOTE_WR,
                "samples_gte": PROMOTE_SAMPLES,
                "windows_gte": PROMOTE_WINDOWS
            },
            "OBSERVE": {"windows_gte": OBSERVE_WINDOWS},
            "REJECT": {"windows_lt": OBSERVE_WINDOWS}
        },
        "global_metrics": all_metrics,
        "groups_total": len(result_rows),
        "promoted": len(promoted),
        "observed": len(observed),
        "rejected": len(rejected),
        "anti_overfit_audit": {
            "p2382_alert": "P2382 may contain survivorship bias",
            "validation_type": "chronological_5_window_walk_forward",
            "learning_during_test": "FORBIDDEN",
            "patch_during_test": "FORBIDDEN",
            "real_execution": "FORBIDDEN",
            "certification": "ONLY_IF_PROMOTED_GT_ZERO_AND_TESTS_PASS"
        },
        "next_mission": "P2384_DE40_INSTITUTIONAL_CYCLE_ENGINE"
    }

    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return summary

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--prev", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    s = run(a.prev, a.out)
    print(json.dumps(s, indent=2, ensure_ascii=False))
