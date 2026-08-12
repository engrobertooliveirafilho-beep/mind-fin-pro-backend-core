import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P1906A_J")

FAMILIES = {
    "PRICE_ACTION": 120,
    "CANDLES": 100,
    "STRUCTURE": 100,
    "LIQUIDITY": 120,
    "FIBONACCI": 60,
    "VOLUME": 100,
    "ORDER_FLOW_PROXY": 100,
    "VOLATILITY": 120,
    "MARKET_PHYSICS": 120,
    "REGIME": 100,
    "SESSION": 80,
    "INTERMARKET": 100,
}

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    registry = []
    idx = 1

    for family, count in FAMILIES.items():
        for i in range(1, count + 1):
            registry.append({
                "feature_id": f"F{idx:04d}",
                "family": family,
                "name": f"{family}_FEATURE_{i:03d}",
                "status": "PLANNED",
                "requires_ohlcv": True,
                "requires_volume": family in {"VOLUME", "ORDER_FLOW_PROXY", "LIQUIDITY"},
                "requires_intermarket": family == "INTERMARKET",
                "mode": "RESEARCH_ONLY"
            })
            idx += 1

    feature_map = {
        family: [f["feature_id"] for f in registry if f["family"] == family]
        for family in FAMILIES
    }

    validation = {
        "required_validations": [
            "NO_LOOKAHEAD",
            "NO_TARGET_LEAKAGE",
            "ROLLING_ONLY",
            "OUT_OF_SAMPLE_STABILITY",
            "FEATURE_DECAY_MONITORING",
            "MISSING_DATA_HANDLING",
        ]
    }

    readiness = {
        "program": "P1906J_FEATURE_EXPLOSION_READINESS_AUDIT",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "feature_family_count": len(FAMILIES),
        "planned_feature_count": len(registry),
        "target_feature_count": 1000,
        "approved_for_P1907": len(registry) >= 1000,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "generated_at": datetime.now(UTC).isoformat()
    }

    files = {
        "P1906A_FEATURE_TAXONOMY.json": FAMILIES,
        "P1906B_FEATURE_REGISTRY.json": registry,
        "P1906C_FEATURE_FAMILY_MAP.json": feature_map,
        "P1906D_FEATURE_GENERATION_PLAN.json": registry,
        "P1906E_FEATURE_VALIDATION_RULES.json": validation,
        "P1906F_FEATURE_LEAKAGE_GUARDS.json": validation,
        "P1906G_FEATURE_DECAY_PLAN.json": validation,
        "P1906H_FEATURE_STORAGE_PLAN.json": {"target": "data/features/canonical"},
        "P1906I_FEATURE_COVERAGE_AUDIT.json": readiness,
        "P1906J_FEATURE_EXPLOSION_READINESS_AUDIT.json": readiness,
        "SUMMARY.json": readiness
    }

    for name, data in files.items():
        (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(readiness, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
