import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2001C")
PROBE = Path("_evidence/P2001B/SOURCE_CONNECTOR_PROBE.json")

DEFAULT_BY_CLASS = {
    "FX": ["MT5_DEMO_EXPORT", "DUKASCOPY_COMPATIBLE_EXPORT", "BROKER_HISTORY"],
    "METALS": ["MT5_DEMO_EXPORT", "DUKASCOPY_COMPATIBLE_EXPORT", "BROKER_HISTORY"],
    "CRYPTO": ["PUBLIC_KLINES", "EXCHANGE_OHLCV_EXPORT", "CSV_IMPORT"],
    "INDEX": ["MT5_DEMO_EXPORT", "BROKER_HISTORY", "CSV_IMPORT"],
    "B3": ["MT5_DEMO_EXPORT", "BROKER_HISTORY", "CSV_IMPORT"],
}

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    probe = read_json(PROBE)
    available = {x["connector"]: x["available"] for x in probe}

    unavailable = [x for x in probe if not x["available"]]
    available_rows = [x for x in probe if x["available"]]

    source_policy = {}
    for asset_class, candidates in DEFAULT_BY_CLASS.items():
        selected = next((c for c in candidates if available.get(c)), None)
        source_policy[asset_class] = {
            "preferred_source": selected,
            "fallback_sources": [c for c in candidates if c != selected and available.get(c)],
            "unavailable_candidates": [c for c in candidates if not available.get(c)],
            "ready": selected is not None,
        }

    blockers = [
        cls for cls, policy in source_policy.items()
        if not policy["ready"]
    ]

    summary = {
        "program": "P2001C_CONNECTOR_DETAIL_AUDIT",
        "status": "PASS" if not blockers else "BLOCKED",
        "mode": "RESEARCH_ONLY",
        "available_connectors": len(available_rows),
        "unavailable_connectors": len(unavailable),
        "unavailable_connector_names": [x["connector"] for x in unavailable],
        "source_policy_ready_classes": sum(1 for p in source_policy.values() if p["ready"]),
        "source_policy_blocked_classes": blockers,
        "download_executed": False,
        "files_written": False,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "approved_for_P2001D": len(blockers) == 0,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT / "CONNECTOR_DETAIL_AUDIT.json").write_text(
        json.dumps(probe, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "SOURCE_POLICY_BY_ASSET_CLASS.json").write_text(
        json.dumps(source_policy, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
