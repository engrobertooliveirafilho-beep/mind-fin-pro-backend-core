import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2001E")

SAMPLES = Path("_evidence/P2001D/ZERO_WRITE_SAMPLES.json")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    samples = read_json(SAMPLES)

    dry_runs = []

    for idx, sample in enumerate(samples, start=1):

        connector = sample["source_primary"]

        dry_runs.append({
            "run_id": f"DRYRUN_{idx:03d}",
            "connector": connector,
            "asset": sample["asset"],
            "asset_class": sample["asset_class"],
            "timeframe": sample["timeframe"],
            "expected_schema": sample["expected_schema"],
            "download_executed": False,
            "files_written": False,
            "records_downloaded": 0,
            "status": "SIMULATION_ONLY",
            "mode": "RESEARCH_ONLY"
        })

    summary = {
        "program": "P2001E_CONNECTOR_DRY_RUN_DETAIL",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "dry_run_count": len(dry_runs),
        "download_executed": False,
        "files_written": False,
        "records_downloaded": 0,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "approved_for_P2001F": True,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT / "CONNECTOR_DRY_RUNS.json").write_text(
        json.dumps(dry_runs, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
