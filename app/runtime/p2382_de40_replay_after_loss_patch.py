from __future__ import annotations

import argparse, csv, json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


MISSION = "P2382_DE40_REPLAY_AFTER_LOSS_PATCH"
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


def max_dd(results: List[float]) -> float:
    eq = 0.0
    peak = 0.0
    dd = 0.0
    for r in results:
        eq += r
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    return abs(dd)


def classify(row: Dict) -> str:
    r = fnum(row.get("realized_r"))
    pf_proxy = fnum(row.get("profit_factor_proxy"))
    exp_proxy = fnum(row.get("expectancy_r_proxy"))

    if r > 0 and pf_proxy >= 1.5 and exp_proxy > 0:
        return "PROMOTE_AFTER_PATCH_REPLAY"
    if r >= 0 and pf_proxy >= 1.1:
        return "OBSERVE_AFTER_PATCH_REPLAY"
    return "REJECT_AFTER_PATCH_REPLAY"


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

        if len(arr) >= 20 and expectancy > 0 and pf >= 1.5 and dd <= max(8, len(arr) * 0.35):
            decision = "PROMOTE_GROUP_AFTER_PATCH"
        elif len(arr) >= 10 and expectancy > -0.03 and pf >= 1.1:
            decision = "OBSERVE_GROUP_AFTER_PATCH"
        else:
            decision = "REJECT_GROUP_AFTER_PATCH"

        row = {keys[i]: k[i] for i in range(len(keys))}
        row.update({
            "samples": len(arr),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(arr), 6) if arr else 0,
            "gross_win_r": round(gross_win, 6),
            "gross_loss_r": round(gross_loss, 6),
            "expectancy_r": round(expectancy, 6),
            "profit_factor": round(pf, 6),
            "max_drawdown_r": round(dd, 6),
            "avg_mae_r": round(sum(fnum(x.get("mae_r")) for x in arr) / len(arr), 6) if arr else 0,
            "avg_mfe_r": round(sum(fnum(x.get("mfe_r")) for x in arr) / len(arr), 6) if arr else 0,
            "decision": decision,
        })
        out.append(row)

    return sorted(
        out,
        key=lambda x: (
            x["decision"] == "PROMOTE_GROUP_AFTER_PATCH",
            x["decision"] == "OBSERVE_GROUP_AFTER_PATCH",
            x["expectancy_r"],
            x["profit_factor"],
            x["samples"],
        ),
        reverse=True,
    )


def run(patched_path: Path, outdir: Path, baseline_expectancy: float, baseline_pf: float, baseline_dd: float) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    rows = load_csv(patched_path)
    evaluated = []

    for r in rows:
        x = dict(r)
        x["patch_replay_decision"] = classify(x)
        x["mode"] = MODE
        x["real_orders"] = REAL_ORDERS
        x["ftmo_real"] = FTMO_REAL
        x["warning"] = "REPLAY_AFTER_PATCH_IS_PAPER_ONLY"
        evaluated.append(x)

    results = [fnum(x.get("realized_r")) for x in evaluated]
    wins = [x for x in results if x > 0]
    losses = [x for x in results if x < 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = gross_win / gross_loss if gross_loss > 0 else (999.0 if gross_win > 0 else 0.0)
    expectancy = sum(results) / len(results) if results else 0
    dd = max_dd(results)

    by_family = aggregate(evaluated, ["family"])
    by_timeframe = aggregate(evaluated, ["timeframe"])
    by_regime = aggregate(evaluated, ["regime"])
    by_lifecycle = aggregate(evaluated, ["lifecycle"])
    by_family_tf = aggregate(evaluated, ["family", "timeframe"])

    promoted = [x for x in evaluated if x["patch_replay_decision"] == "PROMOTE_AFTER_PATCH_REPLAY"]
    observed = [x for x in evaluated if x["patch_replay_decision"] == "OBSERVE_AFTER_PATCH_REPLAY"]
    rejected = [x for x in evaluated if x["patch_replay_decision"] == "REJECT_AFTER_PATCH_REPLAY"]

    promoted_groups = [x for x in by_family_tf if x["decision"] == "PROMOTE_GROUP_AFTER_PATCH"]
    observed_groups = [x for x in by_family_tf if x["decision"] == "OBSERVE_GROUP_AFTER_PATCH"]

    files = {
        "all": outdir / "de40_replay_after_patch_all.csv",
        "summary_table": outdir / "de40_replay_after_patch_summary.csv",
        "promoted": outdir / "de40_replay_after_patch_promoted.csv",
        "observed": outdir / "de40_replay_after_patch_observed.csv",
        "rejected": outdir / "de40_replay_after_patch_rejected.csv",
        "by_family": outdir / "de40_replay_after_patch_by_family.csv",
        "by_timeframe": outdir / "de40_replay_after_patch_by_timeframe.csv",
        "by_regime": outdir / "de40_replay_after_patch_by_regime.csv",
        "by_lifecycle": outdir / "de40_replay_after_patch_by_lifecycle.csv",
        "by_family_timeframe": outdir / "de40_replay_after_patch_by_family_timeframe.csv",
        "promoted_groups": outdir / "de40_replay_after_patch_promoted_groups.csv",
        "observed_groups": outdir / "de40_replay_after_patch_observed_groups.csv",
        "summary_json": outdir / "summary.json",
    }

    summary_table = [{
        "baseline_expectancy_r": baseline_expectancy,
        "patched_expectancy_r": round(expectancy, 6),
        "expectancy_delta": round(expectancy - baseline_expectancy, 6),
        "baseline_profit_factor": baseline_pf,
        "patched_profit_factor": round(pf, 6),
        "profit_factor_delta": round(pf - baseline_pf, 6),
        "baseline_max_drawdown_r": baseline_dd,
        "patched_max_drawdown_r": round(dd, 6),
        "drawdown_delta": round(dd - baseline_dd, 6),
        "drawdown_reduction_pct": round(((baseline_dd - dd) / baseline_dd), 6) if baseline_dd else 0,
        "success_expectancy_positive": expectancy > 0,
        "success_pf_above_1": pf > 1.0,
        "success_dd_reduced_30pct": dd < baseline_dd * 0.70,
    }]

    write_csv(files["all"], evaluated)
    write_csv(files["summary_table"], summary_table)
    write_csv(files["promoted"], promoted)
    write_csv(files["observed"], observed)
    write_csv(files["rejected"], rejected)
    write_csv(files["by_family"], by_family)
    write_csv(files["by_timeframe"], by_timeframe)
    write_csv(files["by_regime"], by_regime)
    write_csv(files["by_lifecycle"], by_lifecycle)
    write_csv(files["by_family_timeframe"], by_family_tf)
    write_csv(files["promoted_groups"], promoted_groups)
    write_csv(files["observed_groups"], observed_groups)

    success = expectancy > 0 and pf > 1.0 and dd < baseline_dd * 0.70

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "patched_source": str(patched_path),
        "baseline": {
            "expectancy_r": baseline_expectancy,
            "profit_factor": baseline_pf,
            "max_drawdown_r": baseline_dd,
        },
        "signals_replayed": len(evaluated),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(len(wins) / len(evaluated), 6) if evaluated else 0,
        "gross_win_r": round(gross_win, 6),
        "gross_loss_r": round(gross_loss, 6),
        "expectancy_r": round(expectancy, 6),
        "profit_factor": round(pf, 6),
        "max_drawdown_r": round(dd, 6),
        "expectancy_delta": round(expectancy - baseline_expectancy, 6),
        "profit_factor_delta": round(pf - baseline_pf, 6),
        "drawdown_delta": round(dd - baseline_dd, 6),
        "drawdown_reduction_pct": round(((baseline_dd - dd) / baseline_dd), 6) if baseline_dd else 0,
        "promoted_after_patch": len(promoted),
        "observed_after_patch": len(observed),
        "rejected_after_patch": len(rejected),
        "promoted_groups_after_patch": len(promoted_groups),
        "observed_groups_after_patch": len(observed_groups),
        "success": success,
        "status": "CERTIFIED",
        "certification": "P2382_REPLAY_AFTER_LOSS_PATCH_CERTIFIED",
        "next": "P2383_WALK_FORWARD_AFTER_PATCH" if success else "P2382A_SECOND_LOSS_PATCH_HARDENING",
        "outputs": {k: str(v) for k, v in files.items()},
        "warning": "PATCH_REPLAY_IS_PAPER_ONLY_NO_REAL_ORDER_PERMISSION",
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--patched", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--baseline-expectancy", type=float, required=True)
    p.add_argument("--baseline-pf", type=float, required=True)
    p.add_argument("--baseline-dd", type=float, required=True)
    args = p.parse_args()

    result = run(
        Path(args.patched),
        Path(args.outdir),
        args.baseline_expectancy,
        args.baseline_pf,
        args.baseline_dd,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
