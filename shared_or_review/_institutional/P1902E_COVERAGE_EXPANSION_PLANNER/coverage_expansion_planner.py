from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


IN = Path("_evidence/P1902D/DATA_COVERAGE_MATRIX.json")
OUT = Path("_evidence/P1902E")

ROADMAP_ASSETS = [
    "EURUSD", "GBPUSD", "USDCAD", "AUDUSD", "NZDUSD", "USDCHF", "USDJPY",
    "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD",
    "NAS100", "SP500", "DAX", "NIKKEI", "WIN", "WDO"
]

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

SOURCE_PLAN = {
    "FX": ["MT5_DEMO_EXPORT", "DUKASCOPY_COMPATIBLE_EXPORT", "BROKER_HISTORY"],
    "METALS": ["MT5_DEMO_EXPORT", "DUKASCOPY_COMPATIBLE_EXPORT", "BROKER_HISTORY"],
    "CRYPTO": ["EXCHANGE_OHLCV_EXPORT", "PUBLIC_KLINES", "CSV_IMPORT"],
    "INDEX": ["MT5_DEMO_EXPORT", "BROKER_HISTORY", "CSV_IMPORT"],
    "B3": ["MT5_DEMO_EXPORT", "BROKER_HISTORY", "CSV_IMPORT"],
}


def asset_class(asset: str) -> str:
    if asset in {"EURUSD","GBPUSD","USDCAD","AUDUSD","NZDUSD","USDCHF","USDJPY"}:
        return "FX"
    if asset in {"XAUUSD","XAGUSD"}:
        return "METALS"
    if asset in {"BTCUSD","ETHUSD"}:
        return "CRYPTO"
    if asset in {"NAS100","SP500","DAX","NIKKEI"}:
        return "INDEX"
    if asset in {"WIN","WDO"}:
        return "B3"
    return "UNKNOWN"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def priority_for(asset: str, timeframe: str, existing: dict | None) -> str:
    if existing is None:
        if timeframe in {"M1", "M5"}:
            return "P0_MISSING_CRITICAL_INTRADAY"
        if timeframe in {"M15", "M30"}:
            return "P1_MISSING_INTRADAY"
        return "P2_MISSING_HIGHER_TIMEFRAME"

    score = existing.get("coverage_score", 0)

    if score < 25:
        return "P0_EXPAND_IMMEDIATELY"
    if score < 50:
        return "P1_HIGH_PRIORITY"
    if score < 75:
        return "P2_MEDIUM_PRIORITY"
    return "P3_HEALTHY"


def action_for(priority: str) -> str:
    if priority.startswith("P0"):
        return "ACQUIRE_AND_NORMALIZE_NOW"
    if priority.startswith("P1"):
        return "ACQUIRE_NEXT_BATCH"
    if priority.startswith("P2"):
        return "BACKFILL_AFTER_INTRADAY"
    return "MONITOR"


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    matrix_report = read_json(IN)
    matrix = matrix_report["coverage_matrix"]

    existing_map = {
        (row["asset"], row["timeframe"]): row
        for row in matrix
    }

    asset_gaps = []
    timeframe_gaps = []
    expansion_queue = []

    for asset in ROADMAP_ASSETS:
        cls = asset_class(asset)

        for tf in TARGET_TIMEFRAMES:
            current = existing_map.get((asset, tf))
            priority = priority_for(asset, tf, current)

            current_rows = current.get("rows_total", 0) if current else 0
            target_rows = TARGET_ROWS[tf]
            missing_rows = max(0, target_rows - current_rows)

            job = {
                "asset": asset,
                "asset_class": cls,
                "timeframe": tf,
                "current_rows": current_rows,
                "target_rows": target_rows,
                "missing_rows": missing_rows,
                "coverage_score": current.get("coverage_score", 0) if current else 0,
                "dataset_count": current.get("dataset_count", 0) if current else 0,
                "priority": priority,
                "action": action_for(priority),
                "preferred_sources": SOURCE_PLAN.get(cls, ["CSV_IMPORT"]),
                "mode": "RESEARCH_ONLY",
                "real_orders": "FORBIDDEN",
            }

            if priority != "P3_HEALTHY":
                expansion_queue.append(job)

            if current is None:
                asset_gaps.append(job)

            if current is None or current_rows < target_rows:
                timeframe_gaps.append(job)

    priority_rank = {
        "P0_EXPAND_IMMEDIATELY": 0,
        "P0_MISSING_CRITICAL_INTRADAY": 1,
        "P1_HIGH_PRIORITY": 2,
        "P1_MISSING_INTRADAY": 3,
        "P2_MEDIUM_PRIORITY": 4,
        "P2_MISSING_HIGHER_TIMEFRAME": 5,
        "P3_HEALTHY": 6,
    }

    expansion_queue = sorted(
        expansion_queue,
        key=lambda x: (
            priority_rank.get(x["priority"], 99),
            -x["missing_rows"],
            x["asset_class"],
            x["asset"],
            x["timeframe"],
        )
    )

    p0 = [j for j in expansion_queue if j["priority"].startswith("P0")]
    p1 = [j for j in expansion_queue if j["priority"].startswith("P1")]
    p2 = [j for j in expansion_queue if j["priority"].startswith("P2")]

    acquisition_plan = {
        "batch_1_critical_intraday": p0[:30],
        "batch_2_high_priority_intraday": p1[:30],
        "batch_3_missing_assets_and_higher_tf": p2[:50],
    }

    result = {
        "program": "P1902E_COVERAGE_EXPANSION_PLANNER",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "roadmap_asset_count": len(ROADMAP_ASSETS),
        "target_timeframe_count": len(TARGET_TIMEFRAMES),
        "existing_matrix_rows": len(matrix),
        "expansion_jobs": len(expansion_queue),
        "asset_gap_jobs": len(asset_gaps),
        "timeframe_gap_jobs": len(timeframe_gaps),
        "p0_jobs": len(p0),
        "p1_jobs": len(p1),
        "p2_jobs": len(p2),
        "asset_gaps": asset_gaps,
        "timeframe_gaps": timeframe_gaps,
        "expansion_priority_queue": expansion_queue,
        "data_acquisition_plan": acquisition_plan,
        "approved_for_P1902F": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    summary = {
        "program": result["program"],
        "status": result["status"],
        "mode": result["mode"],
        "roadmap_asset_count": result["roadmap_asset_count"],
        "target_timeframe_count": result["target_timeframe_count"],
        "existing_matrix_rows": result["existing_matrix_rows"],
        "expansion_jobs": result["expansion_jobs"],
        "asset_gap_jobs": result["asset_gap_jobs"],
        "timeframe_gap_jobs": result["timeframe_gap_jobs"],
        "p0_jobs": result["p0_jobs"],
        "p1_jobs": result["p1_jobs"],
        "p2_jobs": result["p2_jobs"],
        "approved_for_P1902F": result["approved_for_P1902F"],
        "report": "_evidence/P1902E/COVERAGE_EXPANSION_PLANNER.json",
    }

    (OUT / "ASSET_GAPS.json").write_text(
        json.dumps(asset_gaps, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "TIMEFRAME_GAPS.json").write_text(
        json.dumps(timeframe_gaps, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "EXPANSION_PRIORITY_QUEUE.json").write_text(
        json.dumps(expansion_queue, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "DATA_ACQUISITION_PLAN.json").write_text(
        json.dumps(acquisition_plan, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "COVERAGE_EXPANSION_PLANNER.json").write_text(
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
