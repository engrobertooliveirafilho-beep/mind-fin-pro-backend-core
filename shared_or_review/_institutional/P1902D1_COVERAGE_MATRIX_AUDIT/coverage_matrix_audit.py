from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, UTC


P1902B = Path("_evidence/P1902B/SUMMARY.json")
P1902B_DATASETS = Path("_evidence/P1902B/CANONICAL_DATASETS.json")
P1902C = Path("_evidence/P1902C/DATA_QUALITY_AND_COVERAGE_AUDIT.json")
P1902D = Path("_evidence/P1902D/DATA_COVERAGE_MATRIX.json")
OUT = Path("_evidence/P1902D1")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    b = read_json(P1902B)
    b_datasets = read_json(P1902B_DATASETS)
    c = read_json(P1902C)
    d = read_json(P1902D)

    b_assets = set(b.get("canonical_assets", []))
    b_dataset_assets = set(x.get("asset") for x in b_datasets if x.get("asset"))
    c_assets = set(c.get("asset_summary", {}).keys())
    d_assets = set(d.get("asset_summary", {}).keys())

    missing_from_c = sorted(b_assets - c_assets)
    missing_from_d = sorted(b_assets - d_assets)

    by_asset_raw = defaultdict(lambda: {"count": 0, "rows": 0, "timeframes": set()})
    for item in b_datasets:
        asset = item.get("asset")
        if not asset:
            continue
        by_asset_raw[asset]["count"] += 1
        by_asset_raw[asset]["rows"] += int(item.get("rows_estimated") or 0)
        if item.get("timeframe"):
            by_asset_raw[asset]["timeframes"].add(item.get("timeframe"))

    discarded_assets = []
    for asset in sorted(b_assets):
        if asset not in d_assets:
            discarded_assets.append({
                "asset": asset,
                "canonical_dataset_count": by_asset_raw[asset]["count"],
                "canonical_rows": by_asset_raw[asset]["rows"],
                "canonical_timeframes": sorted(by_asset_raw[asset]["timeframes"]),
                "missing_from_P1902C": asset in missing_from_c,
                "missing_from_P1902D": asset in missing_from_d,
            })

    result = {
        "program": "P1902D1_COVERAGE_MATRIX_AUDIT",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "p1902b_canonical_asset_count": len(b_assets),
        "p1902b_dataset_asset_count": len(b_dataset_assets),
        "p1902c_asset_count": len(c_assets),
        "p1902d_asset_count": len(d_assets),
        "missing_from_P1902C": missing_from_c,
        "missing_from_P1902D": missing_from_d,
        "discarded_assets": discarded_assets,
        "inconsistency_detected": len(missing_from_d) > 0 or len(missing_from_c) > 0,
        "recommended_action": "PATCH_P1902B_CANONICALIZATION_OR_P1902C_ASSET_FILTERING" if (missing_from_d or missing_from_c) else "PROCEED_TO_P1902F",
        "approved_for_P1902F": len(missing_from_d) == 0 and len(missing_from_c) == 0,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    summary = {
        "program": result["program"],
        "status": result["status"],
        "p1902b_canonical_asset_count": result["p1902b_canonical_asset_count"],
        "p1902c_asset_count": result["p1902c_asset_count"],
        "p1902d_asset_count": result["p1902d_asset_count"],
        "missing_from_P1902C_count": len(missing_from_c),
        "missing_from_P1902D_count": len(missing_from_d),
        "inconsistency_detected": result["inconsistency_detected"],
        "approved_for_P1902F": result["approved_for_P1902F"],
        "recommended_action": result["recommended_action"],
        "report": "_evidence/P1902D1/COVERAGE_MATRIX_AUDIT.json",
    }

    (OUT / "COVERAGE_MATRIX_AUDIT.json").write_text(
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
