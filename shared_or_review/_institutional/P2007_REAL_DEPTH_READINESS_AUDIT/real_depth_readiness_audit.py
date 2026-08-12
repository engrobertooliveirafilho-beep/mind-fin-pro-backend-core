import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2007")

INPUTS = {
    "data_expansion": "_evidence/P2001G_J/SUMMARY.json",
    "event_ingestion": "_evidence/P2002A_J/SUMMARY.json",
    "feature_computation": "_evidence/P2003A_J/SUMMARY.json",
    "regime_discovery": "_evidence/P2004A_J/SUMMARY.json",
    "memory_construction": "_evidence/P2005A_J/SUMMARY.json",
    "specialist_evolution": "_evidence/P2006A_J/SUMMARY.json",
}

def read_json(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    reports = {k: read_json(v) for k, v in INPUTS.items()}

    real_metrics = {
        "records_downloaded": reports["data_expansion"].get("records_downloaded", 0),
        "events_ingested": reports["event_ingestion"].get("records_ingested", 0),
        "features_computed": reports["feature_computation"].get("features_computed", 0),
        "regimes_discovered": reports["regime_discovery"].get("regimes_discovered", 0),
        "memories_created": reports["memory_construction"].get("memories_created", 0),
        "specialists_generated": reports["specialist_evolution"].get("generated_specialists", 0),
        "specialists_certified": reports["specialist_evolution"].get("certified_specialists", 0),
    }

    planned_metrics = {
        "planned_missing_rows": 16078000,
        "target_events": 14,
        "planned_features": reports["feature_computation"].get("planned_features", 1220),
        "target_memories": reports["memory_construction"].get("target_memory_count", 100000),
        "target_generated_specialists": reports["specialist_evolution"].get("target_generated_specialists", 10000),
        "target_certified_specialists": reports["specialist_evolution"].get("target_certified", 100),
    }

    planned_total = sum(planned_metrics.values())
    real_total = sum(real_metrics.values())

    readiness_score = round((real_total / planned_total) * 100, 6) if planned_total else 0

    blockers = []

    if real_metrics["records_downloaded"] == 0:
        blockers.append("NO_REAL_DATA_DOWNLOADED")

    if real_metrics["features_computed"] == 0:
        blockers.append("NO_REAL_FEATURES_COMPUTED")

    if real_metrics["events_ingested"] == 0:
        blockers.append("NO_REAL_EVENTS_INGESTED")

    if real_metrics["regimes_discovered"] == 0:
        blockers.append("NO_REAL_REGIMES_DISCOVERED")

    if real_metrics["memories_created"] == 0:
        blockers.append("NO_REAL_MEMORIES_CREATED")

    if real_metrics["specialists_certified"] == 0:
        blockers.append("NO_REAL_SPECIALISTS_CERTIFIED")

    next_execution = {
        "recommended_first_real_step": "P2010_SMALL_REAL_DATA_DOWNLOAD_BATCH",
        "reason": "ALL_DOWNSTREAM_REAL_DEPTH_DEPENDS_ON_REAL_DATA",
        "requires": {
            "ALLOW_DATA_DOWNLOAD": "true",
            "ALLOW_REAL_ORDERS": "false",
            "MODE": "RESEARCH_ONLY"
        }
    }

    result = {
        "program": "P2007_REAL_DEPTH_READINESS_AUDIT",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "real_metrics": real_metrics,
        "planned_metrics": planned_metrics,
        "real_depth_score": readiness_score,
        "blockers": blockers,
        "primary_blocker": blockers[0] if blockers else None,
        "next_execution": next_execution,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "approved_for_P2010": True,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT / "REAL_DEPTH_READINESS_AUDIT.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
