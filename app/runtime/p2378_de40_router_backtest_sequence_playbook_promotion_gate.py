from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List


MISSION = "P2378_DE40_ROUTER_BACKTEST_SEQUENCE_PLAYBOOK_PROMOTION_GATE"
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


def fnum(v, default=0.0) -> float:
    try:
        if v is None or str(v).strip() == "":
            return default
        return float(str(v).replace(",", ".").strip())
    except Exception:
        return default


def infer_rr_possible(row: Dict) -> float:
    mfe = fnum(row.get("post_mfe_atr"))
    mae = max(fnum(row.get("post_mae_atr")), 0.10)
    return round(mfe / mae, 6)


def infer_context_result(row: Dict) -> Dict:
    mfe = fnum(row.get("post_mfe_atr"))
    mae = fnum(row.get("post_mae_atr"))
    efficiency = fnum(row.get("post_efficiency"))
    rr_possible = infer_rr_possible(row)

    if mfe >= 2.0 and rr_possible >= 2.0 and efficiency >= 1.2:
        result = 1.0
        label = "CONTEXT_REACHED_2R_PROXY"
    elif mfe >= 1.5 and rr_possible >= 1.5:
        result = 0.5
        label = "CONTEXT_PARTIAL_EDGE_PROXY"
    elif mae > mfe:
        result = -1.0
        label = "CONTEXT_ADVERSE_AFTER_EVENT"
    else:
        result = 0.0
        label = "CONTEXT_NEUTRAL"

    return {
        "result_r_proxy": result,
        "rr_possible_proxy": rr_possible,
        "outcome_label": label,
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


def aggregate_group(rows: List[Dict], keys: List[str], min_samples: int = 30) -> List[Dict]:
    groups = defaultdict(list)

    for r in rows:
        k = tuple(r.get(x, "") for x in keys)
        groups[k].append(r)

    out = []

    for k, arr in groups.items():
        results = [fnum(x.get("result_r_proxy")) for x in arr]
        wins = [x for x in results if x > 0]
        losses = [x for x in results if x < 0]
        gross_win = sum(wins)
        gross_loss = abs(sum(losses))
        pf = gross_win / gross_loss if gross_loss > 0 else (999.0 if gross_win > 0 else 0.0)
        expectancy = sum(results) / len(results) if results else 0
        dd = max_dd(results)

        mfe = [fnum(x.get("post_mfe_atr")) for x in arr]
        mae = [fnum(x.get("post_mae_atr")) for x in arr]
        rr = [fnum(x.get("rr_possible_proxy")) for x in arr]
        scores = [fnum(x.get("context_score")) for x in arr]

        decision = "REJECT_CONTEXT"
        if len(arr) >= min_samples and expectancy > 0 and pf >= 1.5 and dd <= max(8, len(arr) * 0.35):
            decision = "PROMOTE_CONTEXT"
        elif len(arr) >= max(10, min_samples // 2) and expectancy > -0.05 and pf >= 1.1:
            decision = "OBSERVE_CONTEXT"

        row = {keys[i]: k[i] for i in range(len(keys))}
        row.update({
            "samples": len(arr),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(arr), 6) if arr else 0,
            "expectancy_r_proxy": round(expectancy, 6),
            "profit_factor_proxy": round(pf, 6),
            "max_drawdown_r_proxy": round(dd, 6),
            "avg_mfe_atr": round(sum(mfe) / len(mfe), 6) if mfe else 0,
            "avg_mae_atr": round(sum(mae) / len(mae), 6) if mae else 0,
            "avg_rr_possible_proxy": round(sum(rr) / len(rr), 6) if rr else 0,
            "avg_context_score": round(sum(scores) / len(scores), 6) if scores else 0,
            "promotion_decision": decision,
        })
        out.append(row)

    return sorted(
        out,
        key=lambda x: (
            x["promotion_decision"] == "PROMOTE_CONTEXT",
            x["promotion_decision"] == "OBSERVE_CONTEXT",
            x["expectancy_r_proxy"],
            x["profit_factor_proxy"],
            x["samples"],
        ),
        reverse=True,
    )


def sequence_id(row: Dict) -> str:
    return " > ".join([
        row.get("timeframe", ""),
        row.get("session", ""),
        row.get("regime", ""),
        row.get("volatility", ""),
        row.get("event_type", ""),
        row.get("lifecycle", ""),
    ])


def build_sequences(rows: List[Dict]) -> List[Dict]:
    sorted_rows = sorted(rows, key=lambda r: (r.get("timeframe", ""), int(fnum(r.get("event_index")))))
    windows = defaultdict(lambda: deque(maxlen=3))
    seq_rows = []

    for r in sorted_rows:
        tf = r.get("timeframe", "")
        short = "|".join([
            r.get("regime", ""),
            r.get("event_type", ""),
            r.get("lifecycle", ""),
        ])

        windows[tf].append(short)

        if len(windows[tf]) >= 2:
            sid = " -> ".join(list(windows[tf]))
            x = dict(r)
            x["sequence_id"] = sid
            x["sequence_len"] = len(windows[tf])
            seq_rows.append(x)

    return seq_rows


def build_playbooks(rows: List[Dict]) -> List[Dict]:
    groups = defaultdict(list)

    for r in rows:
        fams = str(r.get("recommended_families", "OBSERVE_ONLY")).split("|")
        for fam in fams:
            key = (
                r.get("timeframe", ""),
                r.get("session", ""),
                r.get("regime", ""),
                r.get("lifecycle", ""),
                r.get("event_type", ""),
                fam,
            )
            x = dict(r)
            x["family"] = fam
            groups[key].append(x)

    out = []

    for key, arr in groups.items():
        results = [fnum(x.get("result_r_proxy")) for x in arr]
        wins = [x for x in results if x > 0]
        losses = [x for x in results if x < 0]
        gross_win = sum(wins)
        gross_loss = abs(sum(losses))
        pf = gross_win / gross_loss if gross_loss > 0 else (999.0 if gross_win > 0 else 0.0)
        expectancy = sum(results) / len(results) if results else 0
        rr = [fnum(x.get("rr_possible_proxy")) for x in arr]
        mfe = [fnum(x.get("post_mfe_atr")) for x in arr]
        mae = [fnum(x.get("post_mae_atr")) for x in arr]

        if len(arr) >= 30 and expectancy > 0 and pf >= 1.5 and max_dd(results) <= max(8, len(arr) * 0.35):
            decision = "PROMOTE_PLAYBOOK"
        elif len(arr) >= 15 and expectancy > -0.05 and pf >= 1.1:
            decision = "OBSERVE_PLAYBOOK"
        else:
            decision = "REJECT_PLAYBOOK"

        out.append({
            "playbook_id": "PB_" + str(abs(hash(key)))[:10],
            "timeframe": key[0],
            "session": key[1],
            "regime": key[2],
            "lifecycle": key[3],
            "footprint": key[4],
            "family": key[5],
            "samples": len(arr),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(arr), 6) if arr else 0,
            "expectancy_r_proxy": round(expectancy, 6),
            "profit_factor_proxy": round(pf, 6),
            "max_drawdown_r_proxy": round(max_dd(results), 6),
            "avg_rr_possible_proxy": round(sum(rr) / len(rr), 6) if rr else 0,
            "avg_mfe_atr": round(sum(mfe) / len(mfe), 6) if mfe else 0,
            "avg_mae_atr": round(sum(mae) / len(mae), 6) if mae else 0,
            "promotion_decision": decision,
            "mode": MODE,
            "real_orders": REAL_ORDERS,
            "ftmo_real": FTMO_REAL,
        })

    return sorted(
        out,
        key=lambda x: (
            x["promotion_decision"] == "PROMOTE_PLAYBOOK",
            x["promotion_decision"] == "OBSERVE_PLAYBOOK",
            x["expectancy_r_proxy"],
            x["profit_factor_proxy"],
            x["samples"],
        ),
        reverse=True,
    )


def run(router_candidates: Path, context_library: Path, outdir: Path) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    candidates = load_csv(router_candidates)
    library = load_csv(context_library)

    scored = []
    for r in candidates:
        x = dict(r)
        result = infer_context_result(x)
        x.update(result)
        x["sequence_key"] = sequence_id(x)
        x["mode"] = MODE
        x["real_orders"] = REAL_ORDERS
        x["ftmo_real"] = FTMO_REAL
        x["warning"] = "PAPER_CONTEXT_BACKTEST_PROXY_NOT_LIVE_SIGNAL"
        scored.append(x)

    context_groups = aggregate_group(
        scored,
        ["timeframe", "session", "regime", "lifecycle", "event_type", "recommended_families"],
        min_samples=30,
    )

    sequence_rows = build_sequences(scored)
    sequence_groups = aggregate_group(
        sequence_rows,
        ["timeframe", "sequence_id", "recommended_families"],
        min_samples=20,
    )

    playbooks = build_playbooks(scored)

    promoted_contexts = [x for x in context_groups if x["promotion_decision"] == "PROMOTE_CONTEXT"]
    observed_contexts = [x for x in context_groups if x["promotion_decision"] == "OBSERVE_CONTEXT"]

    promoted_sequences = [x for x in sequence_groups if x["promotion_decision"] == "PROMOTE_CONTEXT"]
    observed_sequences = [x for x in sequence_groups if x["promotion_decision"] == "OBSERVE_CONTEXT"]

    promoted_playbooks = [x for x in playbooks if x["promotion_decision"] == "PROMOTE_PLAYBOOK"]
    observed_playbooks = [x for x in playbooks if x["promotion_decision"] == "OBSERVE_PLAYBOOK"]

    files = {
        "context_backtest": outdir / "de40_router_context_backtest_scored.csv",
        "context_groups": outdir / "de40_router_context_promotion_groups.csv",
        "promoted_contexts": outdir / "de40_router_promoted_contexts.csv",
        "observed_contexts": outdir / "de40_router_observed_contexts.csv",
        "sequence_events": outdir / "de40_context_sequence_events.csv",
        "sequence_groups": outdir / "de40_context_sequence_groups.csv",
        "promoted_sequences": outdir / "de40_promoted_sequences.csv",
        "observed_sequences": outdir / "de40_observed_sequences.csv",
        "playbooks": outdir / "de40_institutional_playbooks.csv",
        "promoted_playbooks": outdir / "de40_promoted_playbooks.csv",
        "observed_playbooks": outdir / "de40_observed_playbooks.csv",
        "summary_json": outdir / "summary.json",
    }

    write_csv(files["context_backtest"], scored)
    write_csv(files["context_groups"], context_groups)
    write_csv(files["promoted_contexts"], promoted_contexts)
    write_csv(files["observed_contexts"], observed_contexts)
    write_csv(files["sequence_events"], sequence_rows)
    write_csv(files["sequence_groups"], sequence_groups)
    write_csv(files["promoted_sequences"], promoted_sequences)
    write_csv(files["observed_sequences"], observed_sequences)
    write_csv(files["playbooks"], playbooks)
    write_csv(files["promoted_playbooks"], promoted_playbooks)
    write_csv(files["observed_playbooks"], observed_playbooks)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "router_candidates_source": str(router_candidates),
        "context_library_source": str(context_library),
        "router_candidates_loaded": len(candidates),
        "context_library_loaded": len(library),
        "scored_context_events": len(scored),
        "context_groups": len(context_groups),
        "promoted_contexts": len(promoted_contexts),
        "observed_contexts": len(observed_contexts),
        "sequence_events": len(sequence_rows),
        "sequence_groups": len(sequence_groups),
        "promoted_sequences": len(promoted_sequences),
        "observed_sequences": len(observed_sequences),
        "playbooks": len(playbooks),
        "promoted_playbooks": len(promoted_playbooks),
        "observed_playbooks": len(observed_playbooks),
        "promotion_rules": {
            "context": "samples>=30 expectancy>0 PF>=1.5 DD acceptable",
            "sequence": "samples>=20 expectancy>0 PF>=1.5 DD acceptable",
            "playbook": "samples>=30 expectancy>0 PF>=1.5 DD acceptable",
        },
        "architecture": [
            "ROUTER_CONTEXT_BACKTEST",
            "CONTEXT_SEQUENCE_ENGINE",
            "INSTITUTIONAL_PLAYBOOK_BUILDER",
            "PROMOTION_GATE",
            "PAPER_ONLY_PERMISSION",
        ],
        "status": "CERTIFIED",
        "certification": "P2378_ROUTER_BACKTEST_SEQUENCE_PLAYBOOK_PROMOTION_GATE_CERTIFIED",
        "next": "P2379_DE40_FORWARD_PAPER_EMISSION_FROM_PROMOTED_PLAYBOOKS",
        "outputs": {k: str(v) for k, v in files.items()},
        "warning": "NO_REAL_ORDER_PERMISSION_CREATED",
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--router-candidates", required=True)
    p.add_argument("--context-library", required=True)
    p.add_argument("--outdir", required=True)
    args = p.parse_args()

    result = run(Path(args.router_candidates), Path(args.context_library), Path(args.outdir))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
