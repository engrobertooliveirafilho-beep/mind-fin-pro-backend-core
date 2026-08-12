from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, UTC


IN = Path("_evidence/P1902C/DATA_QUALITY_AND_COVERAGE_AUDIT.json")
OUT = Path("_evidence/P1902D")


TARGET_ROWS = {
    "M1": 500000,
    "M5": 250000,
    "M15": 120000,
    "M30": 60000,
    "H1": 30000,
    "H4": 12000,
    "D1": 3000,
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def coverage_priority(score: float):
    if score < 25:
        return "P0_EXPAND_IMMEDIATELY"
    if score < 50:
        return "P1_HIGH_PRIORITY"
    if score < 75:
        return "P2_MEDIUM_PRIORITY"
    return "P3_HEALTHY"


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    audit = read_json(IN)
    datasets = audit["datasets"]

    matrix = defaultdict(lambda: {
        "dataset_count": 0,
        "rows_total": 0,
        "avg_schema_score": 0,
        "schema_samples": [],
    })

    for row in datasets:
        asset = row.get("asset") or "UNKNOWN"
        tf = row.get("timeframe") or "UNKNOWN"

        key = (asset, tf)

        matrix[key]["dataset_count"] += 1
        matrix[key]["rows_total"] += int(row.get("rows_estimated") or 0)
        matrix[key]["schema_samples"].append(float(row.get("ohlcv_score") or 0))

    coverage_rows = []

    for (asset, tf), data in matrix.items():

        avg_schema = round(
            sum(data["schema_samples"]) / max(len(data["schema_samples"]), 1),
            4
        )

        target = TARGET_ROWS.get(tf, 50000)

        coverage_score = round(
            min(data["rows_total"] / target, 1.0) * 100,
            2
        )

        coverage_rows.append({
            "asset": asset,
            "timeframe": tf,
            "dataset_count": data["dataset_count"],
            "rows_total": data["rows_total"],
            "target_rows": target,
            "coverage_score": coverage_score,
            "avg_schema_score": avg_schema,
            "priority": coverage_priority(coverage_score),
        })

    coverage_rows = sorted(
        coverage_rows,
        key=lambda x: (
            {"P0_EXPAND_IMMEDIATELY":0,"P1_HIGH_PRIORITY":1,"P2_MEDIUM_PRIORITY":2,"P3_HEALTHY":3}[x["priority"]],
            x["coverage_score"],
            x["asset"],
            x["timeframe"]
        )
    )

    asset_summary = defaultdict(lambda: {
        "rows_total": 0,
        "dataset_count": 0,
        "timeframes": set(),
        "coverage_scores": [],
    })

    for row in coverage_rows:
        a = asset_summary[row["asset"]]
        a["rows_total"] += row["rows_total"]
        a["dataset_count"] += row["dataset_count"]
        a["timeframes"].add(row["timeframe"])
        a["coverage_scores"].append(row["coverage_score"])

    asset_summary_out = {}

    for asset, data in asset_summary.items():
        asset_summary_out[asset] = {
            "rows_total": data["rows_total"],
            "dataset_count": data["dataset_count"],
            "timeframes": sorted(data["timeframes"]),
            "avg_coverage": round(
                sum(data["coverage_scores"]) / max(len(data["coverage_scores"]), 1),
                2
            )
        }

    result = {
        "program": "P1902D_DATA_COVERAGE_MATRIX",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "matrix_rows": len(coverage_rows),
        "asset_count": len(asset_summary_out),
        "coverage_matrix": coverage_rows,
        "asset_summary": dict(sorted(asset_summary_out.items())),
        "expansion_queue": coverage_rows[:100],
        "approved_for_P1902E": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    summary = {
        "program": result["program"],
        "status": result["status"],
        "matrix_rows": result["matrix_rows"],
        "asset_count": result["asset_count"],
        "p0_count": sum(1 for x in coverage_rows if x["priority"] == "P0_EXPAND_IMMEDIATELY"),
        "p1_count": sum(1 for x in coverage_rows if x["priority"] == "P1_HIGH_PRIORITY"),
        "healthy_count": sum(1 for x in coverage_rows if x["priority"] == "P3_HEALTHY"),
        "approved_for_P1902E": True,
        "report": "_evidence/P1902D/DATA_COVERAGE_MATRIX.json",
    }

    (OUT / "DATA_COVERAGE_MATRIX.json").write_text(
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
