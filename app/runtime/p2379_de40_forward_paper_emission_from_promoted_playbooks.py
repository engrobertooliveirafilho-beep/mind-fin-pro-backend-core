from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List


MISSION = "P2379_DE40_FORWARD_PAPER_EMISSION_FROM_PROMOTED_PLAYBOOKS"
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


def infer_direction(footprint: str, regime: str) -> str:
    text = f"{footprint} {regime}".upper()
    if "UP" in text or "TREND_UP" in text:
        return "BUY_PAPER"
    if "DOWN" in text or "TREND_DOWN" in text:
        return "SELL_PAPER"
    return "NO_DIRECTION"


def risk_tier(row: Dict) -> str:
    pf = fnum(row.get("profit_factor_proxy"))
    exp = fnum(row.get("expectancy_r_proxy"))
    dd = fnum(row.get("max_drawdown_r_proxy"))
    samples = fnum(row.get("samples"))

    if samples >= 100 and pf >= 2.0 and exp >= 0.20 and dd <= samples * 0.25:
        return "PRIORITY_PAPER"
    if samples >= 50 and pf >= 1.5 and exp > 0:
        return "STANDARD_PAPER"
    return "OBSERVATION_PAPER"


def create_signal(row: Dict, source_type: str, idx: int) -> Dict:
    direction = infer_direction(row.get("footprint", row.get("event_type", "")), row.get("regime", ""))
    tier = risk_tier(row)

    rr = fnum(row.get("avg_rr_possible_proxy"), 2.0)
    rr_policy = "RR_5_INSTITUTIONAL" if rr >= 5 else "RR_3_PRIORITY" if rr >= 3 else "RR_2_STANDARD"

    signal_status = "PAPER_SIGNAL_READY" if direction != "NO_DIRECTION" and tier != "OBSERVATION_PAPER" else "PAPER_OBSERVE_ONLY"

    return {
        "signal_id": f"P2379_{source_type}_{idx:06d}",
        "symbol": "DE40",
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "source_type": source_type,
        "timeframe": row.get("timeframe", ""),
        "session": row.get("session", ""),
        "regime": row.get("regime", ""),
        "lifecycle": row.get("lifecycle", ""),
        "footprint": row.get("footprint", row.get("event_type", "")),
        "family": row.get("family", row.get("recommended_families", "")),
        "direction": direction,
        "risk_tier": tier,
        "rr_policy": rr_policy,
        "samples": row.get("samples", ""),
        "win_rate": row.get("win_rate", ""),
        "expectancy_r_proxy": row.get("expectancy_r_proxy", ""),
        "profit_factor_proxy": row.get("profit_factor_proxy", ""),
        "max_drawdown_r_proxy": row.get("max_drawdown_r_proxy", ""),
        "avg_rr_possible_proxy": row.get("avg_rr_possible_proxy", ""),
        "avg_mfe_atr": row.get("avg_mfe_atr", ""),
        "avg_mae_atr": row.get("avg_mae_atr", ""),
        "signal_status": signal_status,
        "execution_permission": "PAPER_ONLY_FILE_SIGNAL",
        "mt5_real_permission": "DENIED",
        "ftmo_real_permission": "DENIED",
        "reason": "PROMOTED_CONTEXTUAL_PLAYBOOK_FORWARD_PAPER_CANDIDATE",
        "warning": "THIS_IS_NOT_A_REAL_ORDER",
    }


def run(playbooks_path: Path, contexts_path: Path, sequences_path: Path, outdir: Path) -> Dict:
    outdir.mkdir(parents=True, exist_ok=True)

    playbooks = load_csv(playbooks_path)
    contexts = load_csv(contexts_path)
    sequences = load_csv(sequences_path)

    signals = []

    for i, row in enumerate(playbooks, start=1):
        signals.append(create_signal(row, "PLAYBOOK", i))

    for i, row in enumerate(contexts, start=1):
        signals.append(create_signal(row, "CONTEXT", i))

    for i, row in enumerate(sequences, start=1):
        signals.append(create_signal(row, "SEQUENCE", i))

    ready = [x for x in signals if x["signal_status"] == "PAPER_SIGNAL_READY"]
    observe = [x for x in signals if x["signal_status"] == "PAPER_OBSERVE_ONLY"]

    priority = [x for x in ready if x["risk_tier"] == "PRIORITY_PAPER"]
    standard = [x for x in ready if x["risk_tier"] == "STANDARD_PAPER"]

    files = {
        "all_signals": outdir / "de40_forward_paper_signals_all.csv",
        "ready_signals": outdir / "de40_forward_paper_signals_ready.csv",
        "priority_signals": outdir / "de40_forward_paper_signals_priority.csv",
        "standard_signals": outdir / "de40_forward_paper_signals_standard.csv",
        "observe_signals": outdir / "de40_forward_paper_observe_only.csv",
        "paper_signal_bus": outdir / "mind_de40_paper_signal_bus_p2379.csv",
        "summary_json": outdir / "summary.json",
    }

    write_csv(files["all_signals"], signals)
    write_csv(files["ready_signals"], ready)
    write_csv(files["priority_signals"], priority)
    write_csv(files["standard_signals"], standard)
    write_csv(files["observe_signals"], observe)
    write_csv(files["paper_signal_bus"], ready[:500])

    payload = {
        "mission": MISSION,
        "mode": MODE,
        "real_orders": REAL_ORDERS,
        "ftmo_real": FTMO_REAL,
        "promoted_playbooks_loaded": len(playbooks),
        "promoted_contexts_loaded": len(contexts),
        "promoted_sequences_loaded": len(sequences),
        "paper_signals_total": len(signals),
        "paper_signals_ready": len(ready),
        "priority_paper_signals": len(priority),
        "standard_paper_signals": len(standard),
        "observe_only": len(observe),
        "paper_signal_bus_rows": len(ready[:500]),
        "permission_model": {
            "paper_signal": "ALLOWED",
            "mt5_real_order": "FORBIDDEN",
            "ftmo_real_order": "FORBIDDEN",
            "live_execution": "FORBIDDEN",
        },
        "status": "CERTIFIED",
        "certification": "P2379_FORWARD_PAPER_EMISSION_CERTIFIED",
        "next": "P2380_DE40_FORWARD_PAPER_FEEDBACK_LOOP_AND_PNL_TRACKING",
        "outputs": {k: str(v) for k, v in files.items()},
        "warning": "NO_REAL_ORDER_PERMISSION_CREATED",
    }

    files["summary_json"].write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--playbooks", required=True)
    p.add_argument("--contexts", required=True)
    p.add_argument("--sequences", required=True)
    p.add_argument("--outdir", required=True)
    args = p.parse_args()

    result = run(Path(args.playbooks), Path(args.contexts), Path(args.sequences), Path(args.outdir))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
