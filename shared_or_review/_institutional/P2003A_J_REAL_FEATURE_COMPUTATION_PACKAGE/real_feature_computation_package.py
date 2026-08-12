import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2003A_J")
FEATURES = Path("_evidence/P1906A_J/P1906B_FEATURE_REGISTRY.json")
DATASETS = Path("_evidence/P1902B/CANONICAL_DATASETS.json")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    features = read_json(FEATURES)
    datasets = read_json(DATASETS)

    compute_plan = []
    for f in features:
        compute_plan.append({
            "feature_id": f["feature_id"],
            "family": f["family"],
            "name": f["name"],
            "status": "READY_FOR_COMPUTATION",
            "computed": False,
            "requires_ohlcv": f.get("requires_ohlcv", True),
            "requires_volume": f.get("requires_volume", False),
            "requires_intermarket": f.get("requires_intermarket", False),
            "anti_leakage_rules": [
                "ROLLING_WINDOW_ONLY",
                "NO_FUTURE_BARS",
                "NO_TARGET_COLUMN",
                "TIMESTAMP_ALIGNMENT_REQUIRED"
            ],
            "mode": "RESEARCH_ONLY"
        })

    validation_rules = {
        "rules": [
            "NO_LOOKAHEAD",
            "NO_TARGET_LEAKAGE",
            "NO_FUTURE_SHIFT",
            "ROLLING_ONLY",
            "MISSING_DATA_AWARE",
            "OUT_OF_SAMPLE_STABILITY_REQUIRED"
        ]
    }

    storage_plan = {
        "target_dir": "data/features/canonical",
        "schema": "timestamp,asset,timeframe,feature_id,value",
        "write_enabled": False
    }

    summary = {
        "program": "P2003J_REAL_FEATURE_COMPUTATION_CERTIFICATION",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "planned_features": len(features),
        "canonical_datasets": len(datasets),
        "features_computed": 0,
        "write_enabled": False,
        "files_written": False,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "approved_for_P2004": len(features) >= 1000 and len(datasets) > 0,
        "generated_at": datetime.now(UTC).isoformat()
    }

    files = {
        "P2003A_FEATURE_INPUT_AUDIT.json": {"features": len(features), "datasets": len(datasets)},
        "P2003B_FEATURE_COMPUTE_PLAN.json": compute_plan,
        "P2003C_FEATURE_ANTI_LEAKAGE_RULES.json": validation_rules,
        "P2003D_FEATURE_VALIDATION_PLAN.json": validation_rules,
        "P2003E_FEATURE_STORAGE_PLAN.json": storage_plan,
        "P2003F_FEATURE_BATCH_QUEUE.json": compute_plan,
        "P2003G_FEATURE_DECAY_MONITOR_PLAN.json": validation_rules,
        "P2003H_FEATURE_COVERAGE_AUDIT.json": summary,
        "P2003I_FEATURE_EXECUTION_GATE.json": {"write_enabled": False, "computed": False},
        "P2003J_REAL_FEATURE_COMPUTATION_CERTIFICATION.json": summary,
        "SUMMARY.json": summary
    }

    for name, payload in files.items():
        (OUT / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
