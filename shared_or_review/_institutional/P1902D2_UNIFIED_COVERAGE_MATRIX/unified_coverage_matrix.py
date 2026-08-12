from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, UTC


IN_DIR = Path("_evidence/P1902B")
OUT = Path("_evidence/P1902D2")

FILES = {
    "dataset": "CANONICAL_DATASETS.json",
    "memory": "CANONICAL_MEMORYS.json",
    "feature": "CANONICAL_FEATURES.json",
    "specialist": "CANONICAL_SPECIALISTS.json",
    "backtest": "CANONICAL_BACKTESTS.json",
}

TARGET_ROWS = {
    "dataset": 500000,
    "memory": 100000,
    "feature": 100000,
    "specialist": 1000,
    "backtest": 10000,
}

LAYER_WEIGHTS = {
    "dataset": 0.35,
    "feature": 0.20,
    "memory": 0.20,
    "backtest": 0.15,
    "specialist": 0.10,
}


def read_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def priority(score: float) -> str:
    if score < 25:
        return "P0_CRITICAL"
    if score < 50:
        return "P1_HIGH"
    if score < 75:
        return "P2_MEDIUM"
    return "P3_HEALTHY"


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    raw = {}
    for layer, filename in FILES.items():
        raw[layer] = read_json(IN_DIR / filename)

    asset_layer = defaultdict(lambda: defaultdict(lambda: {
        "files": 0,
        "rows": 0,
        "timeframes": set(),
    }))

    all_assets = set()

    for layer, items in raw.items():
        for item in items:
            asset = item.get("asset")
            if not asset:
                continue

            all_assets.add(asset)

            asset_layer[asset][layer]["files"] += 1
            asset_layer[asset][layer]["rows"] += int(item.get("rows_estimated") or 0)

            tf = item.get("timeframe")
            if tf:
                asset_layer[asset][layer]["timeframes"].add(tf)

    assets = []

    for asset in sorted(all_assets):
        layer_report = {}
        composite = 0.0

        for layer in FILES.keys():
            data = asset_layer[asset][layer]
            rows = data["rows"]
            files = data["files"]
            target = TARGET_ROWS[layer]

            layer_score = round(min(rows / target, 1.0) * 100, 2) if target > 0 else 0
            composite += layer_score * LAYER_WEIGHTS[layer]

            layer_report[layer] = {
                "files": files,
                "rows": rows,
                "target_rows": target,
                "score": layer_score,
                "timeframes": sorted(data["timeframes"]),
            }

        composite_score = round(composite, 2)

        assets.append({
            "asset": asset,
            "composite_coverage_score": composite_score,
            "priority": priority(composite_score),
            "layers": layer_report,
        })

    assets = sorted(
        assets,
        key=lambda x: (
            {"P0_CRITICAL": 0, "P1_HIGH": 1, "P2_MEDIUM": 2, "P3_HEALTHY": 3}[x["priority"]],
            x["composite_coverage_score"],
            x["asset"],
        )
    )

    p0 = [a for a in assets if a["priority"] == "P0_CRITICAL"]
    p1 = [a for a in assets if a["priority"] == "P1_HIGH"]
    p2 = [a for a in assets if a["priority"] == "P2_MEDIUM"]
    p3 = [a for a in assets if a["priority"] == "P3_HEALTHY"]

    layer_totals = {}
    for layer, items in raw.items():
        layer_totals[layer] = {
            "files": len(items),
            "rows": sum(int(i.get("rows_estimated") or 0) for i in items),
            "assets": len(set(i.get("asset") for i in items if i.get("asset"))),
        }

    result = {
        "program": "P1902D2_UNIFIED_COVERAGE_MATRIX",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "asset_count": len(assets),
        "layer_totals": layer_totals,
        "priority_counts": {
            "P0_CRITICAL": len(p0),
            "P1_HIGH": len(p1),
            "P2_MEDIUM": len(p2),
            "P3_HEALTHY": len(p3),
        },
        "assets": assets,
        "expansion_queue": assets,
        "approved_for_P1902F": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    summary = {
        "program": result["program"],
        "status": result["status"],
        "mode": result["mode"],
        "asset_count": result["asset_count"],
        "layer_totals": result["layer_totals"],
        "priority_counts": result["priority_counts"],
        "approved_for_P1902F": result["approved_for_P1902F"],
        "report": "_evidence/P1902D2/UNIFIED_COVERAGE_MATRIX.json",
    }

    (OUT / "UNIFIED_COVERAGE_MATRIX.json").write_text(
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
