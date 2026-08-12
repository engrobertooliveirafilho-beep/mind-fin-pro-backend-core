from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, UTC


PLAN = Path("_evidence/P1902H/MASS_NORMALIZATION_PLAN.json")
TARGETS = Path("_evidence/P1902F/DATASET_TARGETS.json")
OUT = Path("_evidence/P1902I")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def phase_for(tf: str, priority: str) -> str:
    if priority == "P0" and tf in {"M1", "M5"}:
        return "PHASE_1_CRITICAL_INTRADAY"
    if priority == "P0":
        return "PHASE_2_INTRADAY_COMPLETION"
    if priority == "P1":
        return "PHASE_3_HIGH_PRIORITY_BACKFILL"
    return "PHASE_4_STRUCTURAL_BACKFILL"


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    plan = read_json(PLAN)
    targets = read_json(TARGETS)

    target_map = {(t["asset"], t["timeframe"]): t for t in targets}

    rebuild_jobs = []
    for batch in plan:
        key = (batch["asset"], batch["timeframe"])
        target = target_map.get(key, {})

        priority = target.get("priority", "P2")
        missing_rows = int(target.get("missing_rows", 0))

        rebuild_jobs.append({
            "asset": batch["asset"],
            "timeframe": batch["timeframe"],
            "phase": phase_for(batch["timeframe"], priority),
            "priority": priority,
            "current_rows": int(target.get("current_rows", 0)),
            "target_rows": int(target.get("target_rows", 0)),
            "missing_rows": missing_rows,
            "normalization_batch_id": batch["batch_id"],
            "target_output_dir": batch["target_output_dir"],
            "required_steps": [
                "ACQUIRE_RAW_HISTORY",
                "NORMALIZE_OHLCV",
                "VALIDATE_SCHEMA",
                "DEDUPLICATE",
                "DETECT_GAPS",
                "WRITE_MANIFEST",
                "REGISTER_CANONICAL_DATASET"
            ],
            "mode": "RESEARCH_ONLY",
            "real_orders": "FORBIDDEN",
        })

    rebuild_jobs = sorted(
        rebuild_jobs,
        key=lambda x: (
            {"PHASE_1_CRITICAL_INTRADAY": 0, "PHASE_2_INTRADAY_COMPLETION": 1, "PHASE_3_HIGH_PRIORITY_BACKFILL": 2, "PHASE_4_STRUCTURAL_BACKFILL": 3}[x["phase"]],
            -x["missing_rows"],
            x["asset"],
            x["timeframe"],
        )
    )

    by_phase = defaultdict(list)
    by_asset = defaultdict(lambda: {"jobs": 0, "missing_rows": 0})

    for job in rebuild_jobs:
        by_phase[job["phase"]].append(job)
        by_asset[job["asset"]]["jobs"] += 1
        by_asset[job["asset"]]["missing_rows"] += job["missing_rows"]

    result = {
        "program": "P1902I_HISTORICAL_DENSITY_REBUILD_PLAN",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "rebuild_job_count": len(rebuild_jobs),
        "phase_counts": {k: len(v) for k, v in sorted(by_phase.items())},
        "asset_rebuild_summary": dict(sorted(by_asset.items())),
        "rows_missing_total": sum(j["missing_rows"] for j in rebuild_jobs),
        "top_30_rebuild_jobs": rebuild_jobs[:30],
        "approved_for_P1902J": True,
        "generated_at": datetime.now(UTC).isoformat(),
        "rebuild_jobs": rebuild_jobs,
    }

    summary = {
        "program": result["program"],
        "status": result["status"],
        "mode": result["mode"],
        "rebuild_job_count": result["rebuild_job_count"],
        "phase_counts": result["phase_counts"],
        "rows_missing_total": result["rows_missing_total"],
        "approved_for_P1902J": result["approved_for_P1902J"],
        "report": "_evidence/P1902I/HISTORICAL_DENSITY_REBUILD_PLAN.json",
    }

    (OUT / "HISTORICAL_DENSITY_REBUILD_PLAN.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
