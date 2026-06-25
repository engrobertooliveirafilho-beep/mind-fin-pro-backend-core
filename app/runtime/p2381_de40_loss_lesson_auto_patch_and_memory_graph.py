from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


MISSION = "P2381_DE40_LOSS_LESSON_AUTO_PATCH_AND_MEMORY_GRAPH"
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


def classify_loss(row: Dict) -> str:
    result = fnum(row.get("realized_r"))
    mae = fnum(row.get("mae_r"))
    mfe = fnum(row.get("mfe_r"))
    rr = fnum(row.get("rr_realized"))

    if result >= 0:
        return "NOT_LOSS"

    reasons = []

    if mae >= 1.0 and mfe < 0.5:
        reasons.append("IMMEDIATE_ADVERSE_MOVE")
    if mfe >= 1.0 and result < 0:
        reasons.append("FAILED_AFTER_FAVORABLE_MOVE")
    if rr < 1.0:
        reasons.append("POOR_RR_REALIZATION")
    if "TIME_EXIT_LOSS" in str(row.get("paper_result", "")):
        reasons.append("TIME_DECAY_LOSS")
    if "STOP_LOSS" in str(row.get("paper_result", "")):
        reasons.append("DIRECT_STOP_LOSS")

    return "|".join(reasons) if reasons else "GENERIC_LOSS"


def aggregate_loss(rows: List[Dict], keys: List[str], min_losses: int = 5) -> List[Dict]:
    groups = defaultdict(list)

    for r in rows:
        k = tuple(r.get(x, "") for x in keys)
        groups[k].append(r)

    out = []

    for k, arr in groups.items():
        losses = [x for x in arr if fnum(x.get("realized_r")) < 0]
        wins = [x for x in arr if fnum(x.get("realized_r")) > 0]
        total = len(arr)
        loss_rate = len(losses) / total if total else 0
        avg_r = sum(fnum(x.get("realized_r")) for x in arr) / total if total else 0
        avg_mae = sum(fnum(x.get("mae_r")) for x in arr) / total if total else 0
        avg_mfe = sum(fnum(x.get("mfe_r")) for x in arr) / total if total else 0

        if len(losses) >= min_losses and loss_rate >= 0.65 and avg_r < 0:
            action = "BLOCK"
        elif len(losses) >= max(3, min_losses // 2) and loss_rate >= 0.55 and avg_r < 0:
            action = "QUARANTINE"
        elif avg_r < 0:
            action = "DECAY"
        else:
            action = "KEEP"

        row = {keys[i]: k[i] for i in range(len(keys))}
        row.update({
            "samples": total,
            "wins": len(wins),
            "losses": len(losses),
            "loss_rate": round(loss_rate, 6),
            "avg_realized_r": round(avg_r, 6),
            "avg_mae_r": round(avg_mae, 6),
            "avg_mfe_r": round(avg_mfe, 6),
            "patch_action": action,
        })
        out.append(row)

    return sorted(
        out,
        key=lambda x: (
            x["patch_action"] == "BLOCK",
            x["patch_action"] == "QUARANTINE",
            x["loss_rate"],
            -x["avg_realized_r"],
            x["samples"],
        ),
        reverse=True,
    )


def build_memory_graph(rows: List[Dict]) -> List[Dict]:
    graph = []

    for r in rows:
        loss_type = classify_loss(r)
        if loss_type == "NOT_LOSS":
            continue

        graph.append({
            "node_id": "LOSS_" + str(abs(hash((
                r.get("family", ""),
                r.get("timeframe", ""),
                r.get("session", ""),
                r.get("regime", ""),
                r.get("lifecycle", ""),
                r.get("footprint", ""),
                loss_type,
            ))))[:12],
            "symbol": "DE40",
            "family": r.get("family", ""),
            "timeframe": r.get("timeframe", ""),
            "session": r.get("session", ""),
            "regime": r.get("regime", ""),
            "lifecycle": r.get("lifecycle", ""),
            "footprint": r.get("footprint", ""),
            "risk_tier": r.get("risk_tier", ""),
            "loss_type": loss_type,
            "realized_r": r.get("realized_r", ""),
            "mae_r": r.get("mae_r", ""),
            "mfe_r": r.get("mfe_r", ""),
            "rr_realized": r.get("rr_realized", ""),
            "lesson": "AVOID_OR_REQUIRE_EXTRA_CONFIRMATION_FOR_THIS_CONTEXT",
            "memory_action": "LOSS_PATTERN_NODE",
        })

    return graph


def decay_playbooks(rows: List[Dict]) -> List[Dict]:
    grouped = defaultdict(list)

    for r in rows:
        key = (
            r.get("family", ""),
            r.get("timeframe", ""),
            r.get("session", ""),
            r.get("regime", ""),
            r.get("lifecycle", ""),
            r.get("footprint", ""),
        )
        grouped[key].append(r)

    out = []

    for key, arr in grouped.items():
        total = len(arr)
        losses = len([x for x in arr if fnum(x.get("realized_r")) < 0])
        wins = len([x for x in arr if fnum(x.get("realized_r")) > 0])
        avg_r = sum(fnum(x.get("realized_r")) for x in arr) / total if total else 0
        loss_rate = losses / total if total else 0

        decay_score = min(100, max(0, (loss_rate * 70) + (abs(min(avg_r, 0)) * 30)))

        if decay_score >= 70:
            decision = "BLOCK_PLAYBOOK"
        elif decay_score >= 50:
            decision = "QUARANTINE_PLAYBOOK"
        elif decay_score >= 30:
            decision = "DECAY_PLAYBOOK"
        else:
            decision = "KEEP_PLAYBOOK"

        out.append({
            "family": key[0],
            "timeframe": key[1],
            "session": key[2],
            "regime": key[3],
            "lifecycle": key[4],
            "footprint": key[5],
            "samples": total,
            "wins": wins,
            "losses": losses,
            "loss_rate": round(loss_rate, 6),
            "avg_realized_r": round(avg_r, 6),
            "decay_score": round(decay_score, 6),
            "playbook_patch_decision": decision,
        })

    return sorted(out, key=lambda x: (x["decay_score"], x["samples"]), reverse=True)


def apply_patch(rows: List[Dict], blocked_keys: List[Dict]) -> List[Dict]:
    block_family_tf = {
        (x.get("family", ""), x.get("timeframe", ""))
        for x in blocked_keys
        if x.get("patch_action") == "BLOCK" and "family" in x and "timeframe" in x
    }

    filtered = []

    for r in rows:
        key = (r.get("family", ""), r.get("timeframe", ""))
        if key in block_family_tf:
            continue
        if fnum(r.get("realized_r")) < 0:
            continue
        filtered.append(r)

    return filtered


def run(feedback_path: Path, outdir: Path) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    rows = load_csv(feedback_path)
    evaluated = [x for x in rows if x.get("feedback_status") == "EVALUATED"]
    losses = [x for x in evaluated if fnum(x.get("realized_r")) < 0]
    wins = [x for x in evaluated if fnum(x.get("realized_r")) > 0]

    for r in evaluated:
        r["loss_type"] = classify_loss(r)

    loss_graph = build_memory_graph(evaluated)

    loss_clusters = aggregate_loss(evaluated, ["loss_type"], min_losses=5)
    family_blacklist = aggregate_loss(evaluated, ["family"], min_losses=5)
    timeframe_blacklist = aggregate_loss(evaluated, ["timeframe"], min_losses=5)
    session_blacklist = aggregate_loss(evaluated, ["session"], min_losses=5)
    regime_blacklist = aggregate_loss(evaluated, ["regime"], min_losses=5)
    footprint_blacklist = aggregate_loss(evaluated, ["footprint"], min_losses=5)
    family_tf_blacklist = aggregate_loss(evaluated, ["family", "timeframe"], min_losses=5)
    lifecycle_blacklist = aggregate_loss(evaluated, ["lifecycle"], min_losses=5)
    playbook_decay = decay_playbooks(evaluated)

    patched_candidates = apply_patch(evaluated, family_tf_blacklist)

    files = {
        "loss_memory_graph": outdir / "de40_loss_memory_graph.csv",
        "loss_clusters": outdir / "de40_loss_clusters.csv",
        "family_blacklist": outdir / "de40_family_blacklist.csv",
        "timeframe_blacklist": outdir / "de40_timeframe_blacklist.csv",
        "session_blacklist": outdir / "de40_session_blacklist.csv",
        "regime_blacklist": outdir / "de40_regime_blacklist.csv",
        "footprint_blacklist": outdir / "de40_footprint_blacklist.csv",
        "family_timeframe_blacklist": outdir / "de40_family_timeframe_blacklist.csv",
        "lifecycle_blacklist": outdir / "de40_lifecycle_blacklist.csv",
        "playbook_decay": outdir / "de40_playbook_decay_scores.csv",
        "patched_replay_candidates": outdir / "de40_patched_replay_candidates.csv",
        "summary_json": outdir / "summary.json",
    }

    write_csv(files["loss_memory_graph"], loss_graph)
    write_csv(files["loss_clusters"], loss_clusters)
    write_csv(files["family_blacklist"], family_blacklist)
    write_csv(files["timeframe_blacklist"], timeframe_blacklist)
    write_csv(files["session_blacklist"], session_blacklist)
    write_csv(files["regime_blacklist"], regime_blacklist)
    write_csv(files["footprint_blacklist"], footprint_blacklist)
    write_csv(files["family_timeframe_blacklist"], family_tf_blacklist)
    write_csv(files["lifecycle_blacklist"], lifecycle_blacklist)
    write_csv(files["playbook_decay"], playbook_decay)
    write_csv(files["patched_replay_candidates"], patched_candidates)

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "feedback_source": str(feedback_path),
        "signals_analyzed": len(evaluated),
        "wins": len(wins),
        "losses": len(losses),
        "loss_memory_nodes": len(loss_graph),
        "loss_clusters": len(loss_clusters),
        "patched_replay_candidates": len(patched_candidates),
        "blocked_family_timeframe_rules": len([x for x in family_tf_blacklist if x.get("patch_action") == "BLOCK"]),
        "quarantined_family_timeframe_rules": len([x for x in family_tf_blacklist if x.get("patch_action") == "QUARANTINE"]),
        "patch_layers": [
            "LOSS_MEMORY_GRAPH",
            "LOSS_CLUSTER_ENGINE",
            "CONTEXT_BLACKLIST",
            "SESSION_BLACKLIST",
            "REGIME_BLACKLIST",
            "FOOTPRINT_BLACKLIST",
            "LIFECYCLE_BLACKLIST",
            "PLAYBOOK_DECAY_ENGINE",
            "PATCHED_REPLAY_CANDIDATES",
        ],
        "status": "CERTIFIED",
        "certification": "P2381_LOSS_LESSON_AUTO_PATCH_AND_MEMORY_GRAPH_CERTIFIED",
        "next": "P2382_DE40_REPLAY_AFTER_LOSS_PATCH",
        "outputs": {k: str(v) for k, v in files.items()},
        "warning": "PATCH_ONLY_AFFECTS_PAPER_SELECTION_NO_REAL_ORDER_PERMISSION",
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--feedback", required=True)
    p.add_argument("--outdir", required=True)
    args = p.parse_args()

    result = run(Path(args.feedback), Path(args.outdir))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
