import csv, json, math
from pathlib import Path
from datetime import datetime
from collections import defaultdict

MODE="PAPER_ONLY"
REAL_ORDERS="FORBIDDEN"
FTMO_REAL="FORBIDDEN"

REQUIRED = [
    "entry_time","family","footprint","lifecycle","regime","session","timeframe",
    "realized_r","mae_r","mfe_r","rr_realized","profit_factor_proxy","expectancy_r_proxy"
]

WINDOWS = 5

AGG_LEVELS = {
    "family": ["family"],
    "regime": ["regime"],
    "session": ["session"],
    "footprint": ["footprint"],
    "lifecycle": ["lifecycle"],
    "timeframe": ["timeframe"],
    "family_regime": ["family","regime"],
    "regime_session": ["regime","session"],
    "footprint_lifecycle": ["footprint","lifecycle"],
    "family_regime_session": ["family","regime","session"],
}

CRITERIA = {
    "pf": 1.5,
    "expectancy": 0.0,
    "winrate": 45.0,
    "samples": 30,
    "promote_windows": 4,
    "observe_windows": 3
}

def safety():
    assert MODE == "PAPER_ONLY"
    assert REAL_ORDERS == "FORBIDDEN"
    assert FTMO_REAL == "FORBIDDEN"

def fnum(x):
    try:
        if x is None or str(x).strip() == "":
            return 0.0
        return float(str(x).replace(",", "."))
    except Exception:
        return 0.0

def parse_time(x):
    s = str(x).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S","%Y-%m-%dT%H:%M:%S","%Y-%m-%d","%d/%m/%Y %H:%M:%S","%d/%m/%Y"):
        try:
            return datetime.strptime(s[:19], fmt)
        except Exception:
            pass
    return datetime.min

def read_csv(path):
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
    n=len(rows)
    rs=[fnum(r.get("realized_r")) for r in rows]
    wins=[x for x in rs if x > 0]
    losses=[x for x in rs if x < 0]
    gw=sum(wins)
    gl=abs(sum(losses))
    pf=999.0 if gl == 0 and gw > 0 else (gw/gl if gl > 0 else 0.0)
    exp=sum(rs)/n if n else 0.0
    wr=(len(wins)/n*100.0) if n else 0.0

    eq=0.0
    peak=0.0
    dd=0.0
    for r in rs:
        eq += r
        peak=max(peak, eq)
        dd=max(dd, peak-eq)

    return {
        "samples": n,
        "wins": len(wins),
        "losses": len(losses),
        "winrate": round(wr,6),
        "pf": round(pf,6),
        "expectancy": round(exp,6),
        "max_dd_r": round(dd,6),
        "gross_win": round(gw,6),
        "gross_loss": round(gl,6)
    }

def gate(m):
    return (
        m["samples"] >= CRITERIA["samples"] and
        m["pf"] >= CRITERIA["pf"] and
        m["expectancy"] > CRITERIA["expectancy"] and
        m["winrate"] >= CRITERIA["winrate"]
    )

def status(passed):
    if passed >= CRITERIA["promote_windows"]:
        return "PROMOTE"
    if passed >= CRITERIA["observe_windows"]:
        return "OBSERVE"
    return "REJECT"

def windows(rows):
    rows=sorted(rows, key=lambda r: parse_time(r.get("entry_time")))
    n=len(rows)
    out=[]
    for i in range(WINDOWS):
        a=math.floor(i*n/WINDOWS)
        b=math.floor((i+1)*n/WINDOWS)
        part=rows[a:b]
        out.append({"id":i+1,"rows":part})
    return out

def key_for(row, cols):
    return " | ".join([f"{c}={row.get(c,'UNKNOWN')}" for c in cols])

def run(p2382, p2383, outdir):
    safety()
    out=Path(outdir)
    out.mkdir(parents=True, exist_ok=True)

    src=Path(p2382) / "de40_replay_after_patch_all.csv"
    if not src.exists():
        raise FileNotFoundError(str(src))

    rows=read_csv(src)
    if not rows:
        raise ValueError("empty input")

    missing=[c for c in REQUIRED if c not in rows[0]]
    if missing:
        raise ValueError(f"missing schema: {missing}")

    win=windows(rows)

    all_results=[]
    promoted=[]
    observed=[]
    rejected=[]

    for level, cols in AGG_LEVELS.items():
        groups=defaultdict(lambda: defaultdict(list))

        for w in win:
            for r in w["rows"]:
                groups[key_for(r, cols)][w["id"]].append(r)

        level_rows=[]

        for k, bywin in groups.items():
            row={
                "aggregation_level": level,
                "aggregation_columns": "+".join(cols),
                "aggregation_key": k,
            }

            passed=0
            total=[]
            for i in range(1, WINDOWS+1):
                part=bywin.get(i, [])
                total.extend(part)
                m=metrics(part)
                ok=gate(m)
                if ok:
                    passed += 1

                row[f"w{i}_samples"]=m["samples"]
                row[f"w{i}_wins"]=m["wins"]
                row[f"w{i}_losses"]=m["losses"]
                row[f"w{i}_winrate"]=m["winrate"]
                row[f"w{i}_pf"]=m["pf"]
                row[f"w{i}_expectancy"]=m["expectancy"]
                row[f"w{i}_passed"]=ok

            gm=metrics(total)
            row["total_samples"]=gm["samples"]
            row["total_wins"]=gm["wins"]
            row["total_losses"]=gm["losses"]
            row["total_winrate"]=gm["winrate"]
            row["total_pf"]=gm["pf"]
            row["total_expectancy"]=gm["expectancy"]
            row["total_dd_r"]=gm["max_dd_r"]
            row["passed_windows"]=passed
            row["status"]=status(passed)

            level_rows.append(row)
            all_results.append(row)

            if row["status"] == "PROMOTE":
                promoted.append(row)
            elif row["status"] == "OBSERVE":
                observed.append(row)
            else:
                rejected.append(row)

        fields=list(level_rows[0].keys()) if level_rows else ["aggregation_level"]
        write_csv(out / f"de40_walk_forward_{level}.csv", level_rows, fields)

    fields=list(all_results[0].keys()) if all_results else ["aggregation_level"]
    write_csv(out / "de40_walk_forward_aggregation_results.csv", all_results, fields)
    write_csv(out / "de40_walk_forward_aggregation_promoted.csv", promoted, fields)
    write_csv(out / "de40_walk_forward_aggregation_observed.csv", observed, fields)
    write_csv(out / "de40_walk_forward_aggregation_rejected.csv", rejected, fields)

    by_level=[]
    for level in AGG_LEVELS:
        subset=[r for r in all_results if r["aggregation_level"] == level]
        by_level.append({
            "aggregation_level": level,
            "groups": len(subset),
            "promoted": len([r for r in subset if r["status"] == "PROMOTE"]),
            "observed": len([r for r in subset if r["status"] == "OBSERVE"]),
            "rejected": len([r for r in subset if r["status"] == "REJECT"]),
            "max_samples": max([r["total_samples"] for r in subset], default=0),
            "max_passed_windows": max([r["passed_windows"] for r in subset], default=0),
        })

    write_csv(out / "de40_walk_forward_aggregation_level_summary.csv", by_level, list(by_level[0].keys()))

    summary={
        "mission":"P2383B_DE40_WALK_FORWARD_AGGREGATION_REPAIR",
        "mode":MODE,
        "real_orders":REAL_ORDERS,
        "ftmo_real":FTMO_REAL,
        "input":str(src),
        "previous_p2383":str(p2383),
        "output":str(out),
        "reason":"P2383 full signature generated 227 groups for 227 signals; Samples>=30 made promotion impossible.",
        "aggregation_levels":AGG_LEVELS,
        "criteria":CRITERIA,
        "global_metrics":metrics(rows),
        "total_results":len(all_results),
        "promoted":len(promoted),
        "observed":len(observed),
        "rejected":len(rejected),
        "level_summary":by_level,
        "certification":"NOT_CERTIFIED" if len(promoted)==0 else "PROMOTED_AGGREGATIONS_FOUND",
        "p2384_allowed": True if len(promoted)>0 else False,
        "safety":"PAPER_ONLY_ONLY_REAL_ORDERS_FORBIDDEN"
    }

    with open(out / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return summary

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--p2382", required=True)
    p.add_argument("--p2383", required=True)
    p.add_argument("--out", required=True)
    a=p.parse_args()
    print(json.dumps(run(a.p2382, a.p2383, a.out), indent=2, ensure_ascii=False))
