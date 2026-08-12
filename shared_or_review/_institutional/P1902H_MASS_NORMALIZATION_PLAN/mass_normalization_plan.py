from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


IN = Path("_evidence/P1902F/NORMALIZATION_JOBS.json")
OUT = Path("_evidence/P1902H")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def batch_id(job: dict) -> str:
    return f'{job["asset"]}_{job["timeframe"]}'


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    jobs = read_json(IN)

    plan = []
    for job in jobs:
        plan.append({
            "batch_id": batch_id(job),
            "asset": job["asset"],
            "timeframe": job["timeframe"],
            "input_source": job["input_source"],
            "target_output_dir": job["target_output_dir"],
            "output_schema": job["output_schema"],
            "validations": job["required_validations"],
            "deduplication": True,
            "gap_detection": True,
            "chronological_sort": True,
            "schema_enforcement": True,
            "quarantine_invalid_rows": True,
            "write_manifest": True,
            "mode": "RESEARCH_ONLY",
            "real_orders": "FORBIDDEN",
        })

    manifests = [
        {
            "asset": p["asset"],
            "timeframe": p["timeframe"],
            "manifest_path": f'{p["target_output_dir"]}/manifest.json',
            "status": "PLANNED",
        }
        for p in plan
    ]

    summary = {
        "program": "P1902H_MASS_NORMALIZATION_PLAN",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "normalization_batches": len(plan),
        "manifest_count": len(manifests),
        "schema": "timestamp,open,high,low,close,volume",
        "approved_for_P1902I": len(plan) > 0,
        "report": "_evidence/P1902H/MASS_NORMALIZATION_PLAN.json",
        "generated_at": datetime.now(UTC).isoformat(),
    }

    (OUT / "MASS_NORMALIZATION_PLAN.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "NORMALIZATION_MANIFESTS.json").write_text(
        json.dumps(manifests, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
