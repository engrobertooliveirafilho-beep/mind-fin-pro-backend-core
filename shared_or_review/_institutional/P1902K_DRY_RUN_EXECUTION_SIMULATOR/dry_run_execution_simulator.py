from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


JOBS = Path("_evidence/P1902I/HISTORICAL_DENSITY_REBUILD_PLAN.json")
OUT = Path("_evidence/P1902K")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    plan = read_json(JOBS)
    jobs = plan.get("rebuild_jobs", [])

    simulated = []
    blockers = []

    for idx, job in enumerate(jobs, start=1):
        target_dir = Path(job["target_output_dir"])
        manifest = target_dir / "manifest.json"

        simulated.append({
            "sequence": idx,
            "asset": job["asset"],
            "timeframe": job["timeframe"],
            "phase": job["phase"],
            "priority": job["priority"],
            "missing_rows": job["missing_rows"],
            "target_output_dir": str(target_dir).replace("\\", "/"),
            "manifest_path": str(manifest).replace("\\", "/"),
            "dry_run_steps": job["required_steps"],
            "status": "DRY_RUN_READY",
            "mode": "RESEARCH_ONLY",
            "real_orders": "FORBIDDEN",
            "download_executed": False,
            "files_written": False,
        })

    if not jobs:
        blockers.append("NO_REBUILD_JOBS")

    summary = {
        "program": "P1902K_DRY_RUN_EXECUTION_SIMULATOR",
        "status": "PASS" if not blockers else "BLOCKED",
        "mode": "RESEARCH_ONLY",
        "dry_run_jobs": len(simulated),
        "download_executed": False,
        "files_written": False,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "blockers": blockers,
        "approved_for_P1902L": len(blockers) == 0,
        "report": "_evidence/P1902K/DRY_RUN_EXECUTION_SIMULATOR.json",
        "generated_at": datetime.now(UTC).isoformat(),
    }

    (OUT / "DRY_RUN_EXECUTION_SIMULATOR.json").write_text(
        json.dumps({"summary": summary, "jobs": simulated}, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
