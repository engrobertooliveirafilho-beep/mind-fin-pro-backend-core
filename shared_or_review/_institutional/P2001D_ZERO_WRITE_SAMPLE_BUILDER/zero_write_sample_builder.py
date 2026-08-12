import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2001D")
DOWNLOAD_JOBS = Path("_evidence/P1902F/DOWNLOAD_JOBS.json")
POLICY = Path("_evidence/P2001C/SOURCE_POLICY_BY_ASSET_CLASS.json")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    jobs = read_json(DOWNLOAD_JOBS)
    policy = read_json(POLICY)

    samples = []
    seen = set()

    for job in jobs:
        cls = job["asset_class"]
        key = (cls, job["source_primary"])
        if key in seen:
            continue
        seen.add(key)

        samples.append({
            "asset_class": cls,
            "asset": job["asset"],
            "timeframe": job["timeframe"],
            "source_primary": job["source_primary"],
            "policy_preferred_source": policy.get(cls, {}).get("preferred_source"),
            "sample_mode": "ZERO_WRITE",
            "download_executed": False,
            "files_written": False,
            "expected_schema": "timestamp,open,high,low,close,volume",
            "real_orders": "FORBIDDEN",
            "status": "SAMPLE_READY"
        })

    summary = {
        "program": "P2001D_ZERO_WRITE_SAMPLE_BUILDER",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "sample_count": len(samples),
        "download_executed": False,
        "files_written": False,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "approved_for_P2001E": len(samples) > 0,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT / "ZERO_WRITE_SAMPLES.json").write_text(
        json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
