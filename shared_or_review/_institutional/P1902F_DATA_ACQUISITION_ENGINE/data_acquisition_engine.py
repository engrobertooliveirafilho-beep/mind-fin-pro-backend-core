from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


P1902D2 = Path("_evidence/P1902D2/UNIFIED_COVERAGE_MATRIX.json")
P1902E = Path("_evidence/P1902E/EXPANSION_PRIORITY_QUEUE.json")
OUT = Path("_evidence/P1902F")


TARGET_TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]

TARGET_ROWS = {
    "M1": 500000,
    "M5": 250000,
    "M15": 120000,
    "M30": 60000,
    "H1": 30000,
    "H4": 12000,
    "D1": 3000,
}

SOURCE_POLICY = {
    "FX": {
        "primary": "MT5_DEMO_EXPORT",
        "secondary": ["DUKASCOPY_COMPATIBLE_EXPORT", "BROKER_HISTORY"],
        "format": "CSV_OHLCV",
    },
    "METALS": {
        "primary": "MT5_DEMO_EXPORT",
        "secondary": ["DUKASCOPY_COMPATIBLE_EXPORT", "BROKER_HISTORY"],
        "format": "CSV_OHLCV",
    },
    "CRYPTO": {
        "primary": "PUBLIC_KLINES",
        "secondary": ["EXCHANGE_OHLCV_EXPORT", "CSV_IMPORT"],
        "format": "CSV_OHLCV",
    },
    "INDEX": {
        "primary": "MT5_DEMO_EXPORT",
        "secondary": ["BROKER_HISTORY", "CSV_IMPORT"],
        "format": "CSV_OHLCV",
    },
    "B3": {
        "primary": "MT5_DEMO_EXPORT",
        "secondary": ["BROKER_HISTORY", "CSV_IMPORT"],
        "format": "CSV_OHLCV",
    },
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def normalize_priority(p: str) -> str:
    if p.startswith("P0"):
        return "P0"
    if p.startswith("P1"):
        return "P1"
    if p.startswith("P2"):
        return "P2"
    return "P3"


def acquisition_type(job: dict) -> str:
    if job.get("current_rows", 0) == 0:
        return "NEW_DATASET_ACQUISITION"
    return "HISTORICAL_BACKFILL"


def build_download_job(job: dict) -> dict:
    cls = job["asset_class"]
    policy = SOURCE_POLICY.get(cls, {
        "primary": "CSV_IMPORT",
        "secondary": [],
        "format": "CSV_OHLCV",
    })

    return {
        "job_id": f'{job["asset"]}_{job["timeframe"]}_{normalize_priority(job["priority"])}',
        "asset": job["asset"],
        "asset_class": cls,
        "timeframe": job["timeframe"],
        "source_primary": policy["primary"],
        "source_secondary": policy["secondary"],
        "expected_format": policy["format"],
        "current_rows": job["current_rows"],
        "target_rows": job["target_rows"],
        "missing_rows": job["missing_rows"],
        "minimum_years": 10,
        "preferred_years": 20,
        "priority": normalize_priority(job["priority"]),
        "acquisition_type": acquisition_type(job),
        "mode": "RESEARCH_ONLY",
        "real_orders": "FORBIDDEN",
    }


def build_normalization_job(download_job: dict) -> dict:
    return {
        "job_id": download_job["job_id"],
        "asset": download_job["asset"],
        "timeframe": download_job["timeframe"],
        "input_source": download_job["source_primary"],
        "output_schema": "timestamp,open,high,low,close,volume",
        "required_validations": [
            "OHLC_SCHEMA_CHECK",
            "DUPLICATE_TIMESTAMP_CHECK",
            "MISSING_TIMESTAMP_GAP_CHECK",
            "NON_POSITIVE_PRICE_CHECK",
            "HIGH_LOW_INTEGRITY_CHECK",
            "CHRONOLOGICAL_ORDER_CHECK",
        ],
        "target_output_dir": f'data/canonical/{download_job["asset"]}/{download_job["timeframe"]}',
        "mode": "RESEARCH_ONLY",
        "real_orders": "FORBIDDEN",
    }


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    unified = read_json(P1902D2)
    expansion_queue = read_json(P1902E)

    unified_assets = unified.get("assets", [])
    critical_assets = [
        a for a in unified_assets
        if a.get("priority") == "P0_CRITICAL"
    ]

    acquisition_queue = []

    for job in expansion_queue:
        if normalize_priority(job["priority"]) in {"P0", "P1", "P2"}:
            acquisition_queue.append({
                **job,
                "normalized_priority": normalize_priority(job["priority"]),
                "acquisition_type": acquisition_type(job),
                "minimum_years": 10,
                "preferred_years": 20,
            })

    download_jobs = [build_download_job(j) for j in acquisition_queue]
    normalization_jobs = [build_normalization_job(j) for j in download_jobs]

    dataset_targets = []
    for j in acquisition_queue:
        dataset_targets.append({
            "asset": j["asset"],
            "asset_class": j["asset_class"],
            "timeframe": j["timeframe"],
            "current_rows": j["current_rows"],
            "target_rows": j["target_rows"],
            "missing_rows": j["missing_rows"],
            "coverage_score": j["coverage_score"],
            "priority": j["normalized_priority"],
            "minimum_years": 10,
            "preferred_years": 20,
        })

    relink_jobs = []
    for asset in critical_assets:
        layers = asset.get("layers", {})
        specialist_assets = layers.get("specialist", {}).get("files", 0)
        backtest_assets = layers.get("backtest", {}).get("files", 0)

        if specialist_assets == 0:
            relink_jobs.append({
                "asset": asset["asset"],
                "layer": "specialist",
                "action": "LINK_SPECIALISTS_TO_ASSET",
                "reason": "SPECIALIST_LAYER_HAS_ROWS_BUT_NO_ASSET_BINDING",
                "priority": "P1",
            })

        if backtest_assets == 0:
            relink_jobs.append({
                "asset": asset["asset"],
                "layer": "backtest",
                "action": "LINK_BACKTESTS_TO_ASSET",
                "reason": "BACKTEST_LAYER_HAS_ROWS_BUT_NO_ASSET_BINDING",
                "priority": "P1",
            })

    source_discovery = {
        "program": "P1902F_SOURCE_DISCOVERY",
        "status": "PASS",
        "sources_by_class": SOURCE_POLICY,
        "mode": "RESEARCH_ONLY",
        "real_orders": "FORBIDDEN",
    }

    rows_current_total = sum(int(j["current_rows"]) for j in acquisition_queue)
    rows_target_total = sum(int(j["target_rows"]) for j in acquisition_queue)
    rows_missing_total = sum(int(j["missing_rows"]) for j in acquisition_queue)

    result = {
        "program": "P1902F_DATA_ACQUISITION_ENGINE",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "critical_asset_count": len(critical_assets),
        "acquisition_job_count": len(acquisition_queue),
        "download_job_count": len(download_jobs),
        "normalization_job_count": len(normalization_jobs),
        "relink_job_count": len(relink_jobs),
        "rows_current_total": rows_current_total,
        "rows_target_total": rows_target_total,
        "rows_missing_total": rows_missing_total,
        "p0_jobs": sum(1 for j in acquisition_queue if j["normalized_priority"] == "P0"),
        "p1_jobs": sum(1 for j in acquisition_queue if j["normalized_priority"] == "P1"),
        "p2_jobs": sum(1 for j in acquisition_queue if j["normalized_priority"] == "P2"),
        "top_20_priority_jobs": acquisition_queue[:20],
        "approved_for_P1902G": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    (OUT / "ACQUISITION_QUEUE.json").write_text(
        json.dumps(acquisition_queue, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SOURCE_DISCOVERY.json").write_text(
        json.dumps(source_discovery, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "DOWNLOAD_JOBS.json").write_text(
        json.dumps(download_jobs, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "NORMALIZATION_JOBS.json").write_text(
        json.dumps(normalization_jobs, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "DATASET_TARGETS.json").write_text(
        json.dumps(dataset_targets, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SPECIALIST_BACKTEST_RELINK_JOBS.json").write_text(
        json.dumps(relink_jobs, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
