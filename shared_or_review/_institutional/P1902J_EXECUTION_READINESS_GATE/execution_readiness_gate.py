from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


REQUIRED_INPUTS = [
    "_evidence/P1902F/DOWNLOAD_JOBS.json",
    "_evidence/P1902F/NORMALIZATION_JOBS.json",
    "_evidence/P1902G/SOURCE_RANKING.json",
    "_evidence/P1902H/MASS_NORMALIZATION_PLAN.json",
    "_evidence/P1902I/HISTORICAL_DENSITY_REBUILD_PLAN.json",
]

REQUIRED_DIRS = [
    "data",
    "data/raw",
    "data/canonical",
    "data/quarantine",
    "data/manifests",
    "_evidence/P1902J",
]


OUT = Path("_evidence/P1902J")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    input_checks = []
    for item in REQUIRED_INPUTS:
        p = Path(item)
        input_checks.append({
            "path": item,
            "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else 0,
        })

    dir_checks = []
    for item in REQUIRED_DIRS:
        p = Path(item)
        p.mkdir(parents=True, exist_ok=True)
        dir_checks.append({
            "path": item,
            "exists": p.exists(),
        })

    download_jobs = read_json(Path("_evidence/P1902F/DOWNLOAD_JOBS.json")) or []
    normalization_jobs = read_json(Path("_evidence/P1902F/NORMALIZATION_JOBS.json")) or []
    rebuild_plan = read_json(Path("_evidence/P1902I/HISTORICAL_DENSITY_REBUILD_PLAN.json")) or {}

    lock_checks = {
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "download_execution": "NOT_STARTED",
        "broker_execution": "FORBIDDEN",
    }

    job_consistency = {
        "download_jobs": len(download_jobs),
        "normalization_jobs": len(normalization_jobs),
        "rebuild_jobs": rebuild_plan.get("rebuild_job_count", 0),
        "consistent": len(download_jobs) == len(normalization_jobs) == rebuild_plan.get("rebuild_job_count", -1),
    }

    blockers = []

    if not all(x["exists"] for x in input_checks):
        blockers.append("MISSING_REQUIRED_INPUTS")

    if not job_consistency["consistent"]:
        blockers.append("JOB_COUNT_MISMATCH")

    if len(download_jobs) == 0:
        blockers.append("NO_DOWNLOAD_JOBS")

    approved = len(blockers) == 0

    result = {
        "program": "P1902J_EXECUTION_READINESS_GATE",
        "status": "PASS" if approved else "BLOCKED",
        "mode": "RESEARCH_ONLY",
        "input_checks": input_checks,
        "dir_checks": dir_checks,
        "lock_checks": lock_checks,
        "job_consistency": job_consistency,
        "blockers": blockers,
        "approved_for_P1902K": approved,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    summary = {
        "program": result["program"],
        "status": result["status"],
        "mode": result["mode"],
        "download_jobs": job_consistency["download_jobs"],
        "normalization_jobs": job_consistency["normalization_jobs"],
        "rebuild_jobs": job_consistency["rebuild_jobs"],
        "consistent": job_consistency["consistent"],
        "blockers": blockers,
        "approved_for_P1902K": result["approved_for_P1902K"],
        "report": "_evidence/P1902J/EXECUTION_READINESS_GATE.json",
    }

    (OUT / "EXECUTION_READINESS_GATE.json").write_text(
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
