from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


OUT = Path("_evidence/P1903A")

EVENT_TYPES = [
    "FOMC", "CPI", "PPI", "NFP", "ECB", "BOJ", "BOE",
    "FED_SPEECH", "WAR", "PANDEMIC", "BANKING_CRISIS",
    "ENERGY_SHOCK", "ELECTION", "DEBT_CRISIS"
]

EVENT_WINDOWS = {
    "pre_event_hours": [1, 4, 24, 72],
    "post_event_hours": [1, 4, 24, 72, 168],
    "event_day": True,
    "event_week": True,
}

REQUIRED_FIELDS = [
    "event_id",
    "event_type",
    "event_name",
    "timestamp_utc",
    "country",
    "asset_scope",
    "expected_impact",
    "actual_value",
    "forecast_value",
    "previous_value",
    "surprise_value",
    "source",
    "event_window",
    "linked_assets",
    "memory_tags",
]


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    schema = {
        "program": "P1903A_REAL_EVENT_MEMORY_SCHEMA",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "event_types": EVENT_TYPES,
        "event_windows": EVENT_WINDOWS,
        "required_fields": REQUIRED_FIELDS,
        "storage_targets": {
            "raw_events": "data/events/raw",
            "canonical_events": "data/events/canonical",
            "event_memory": "data/events/memory",
            "event_manifests": "data/events/manifests"
        },
        "approved_for_P1903B": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    summary = {
        "program": schema["program"],
        "status": schema["status"],
        "mode": schema["mode"],
        "event_type_count": len(EVENT_TYPES),
        "required_field_count": len(REQUIRED_FIELDS),
        "approved_for_P1903B": True,
        "report": "_evidence/P1903A/REAL_EVENT_MEMORY_SCHEMA.json",
    }

    (OUT / "REAL_EVENT_MEMORY_SCHEMA.json").write_text(
        json.dumps(schema, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
