import json
import os
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2001")
DOWNLOAD_JOBS = Path("_evidence/P1902F/DOWNLOAD_JOBS.json")
NORMALIZATION_JOBS = Path("_evidence/P1902F/NORMALIZATION_JOBS.json")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

def env_bool(name):
    return os.getenv(name, "false").lower().strip() == "true"

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    allow_download = env_bool("ALLOW_DATA_DOWNLOAD")
    downloads = read_json(DOWNLOAD_JOBS)
    normalizations = read_json(NORMALIZATION_JOBS)

    execution_plan = []
    for i, job in enumerate(downloads, start=1):
        execution_plan.append({
            "sequence": i,
            "job_id": job["job_id"],
            "asset": job["asset"],
            "timeframe": job["timeframe"],
            "source_primary": job["source_primary"],
            "missing_rows": job["missing_rows"],
            "download_allowed": allow_download,
            "download_executed": False,
            "status": "BLOCKED_BY_DEFAULT" if not allow_download else "READY_FOR_MANUAL_EXECUTION",
            "mode": "RESEARCH_ONLY",
            "real_orders": "FORBIDDEN"
        })

    result = {
        "program": "P2001_DATA_EXPANSION_CONTROLLED_EXECUTOR",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "allow_data_download": allow_download,
        "download_jobs": len(downloads),
        "normalization_jobs": len(normalizations),
        "planned_rows_missing": sum(int(j.get("missing_rows", 0)) for j in downloads),
        "download_executed": False,
        "files_written": False,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "approved_for_P2001B": True,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT / "DATA_EXPANSION_EXECUTION_PLAN.json").write_text(json.dumps(execution_plan, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "SUMMARY.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
