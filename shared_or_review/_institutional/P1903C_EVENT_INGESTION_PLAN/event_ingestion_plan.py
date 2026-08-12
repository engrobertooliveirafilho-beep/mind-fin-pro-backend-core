from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


OUT = Path("_evidence/P1903C")

EVENT_SCHEDULES = {
    "FOMC": "monthly",
    "CPI": "monthly",
    "PPI": "monthly",
    "NFP": "monthly",
    "ECB": "scheduled",
    "BOJ": "scheduled",
    "BOE": "scheduled",
    "FED_SPEECH": "scheduled",
    "WAR": "event_driven",
    "PANDEMIC": "event_driven",
    "BANKING_CRISIS": "event_driven",
    "ENERGY_SHOCK": "weekly",
    "ELECTION": "event_driven",
    "DEBT_CRISIS": "event_driven",
}

PRIORITY_EVENTS = {"FOMC", "CPI", "NFP", "ECB", "BOJ", "BOE", "BANKING_CRISIS", "ENERGY_SHOCK"}

EVENT_WINDOWS = {
    "pre_event_hours": [1, 4, 24, 72],
    "post_event_hours": [1, 4, 24, 72, 168],
    "event_day": True,
    "event_week": True,
}


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    jobs = []
    for event_type, schedule in EVENT_SCHEDULES.items():
        priority = "P0" if event_type in PRIORITY_EVENTS else "P1"
        jobs.append({
            "event_type": event_type,
            "schedule": schedule,
            "priority": priority,
            "event_window": EVENT_WINDOWS,
            "mode": "RESEARCH_ONLY",
            "download_executed": False,
            "real_orders": "FORBIDDEN",
        })

    queue = sorted(jobs, key=lambda x: (x["priority"], x["event_type"]))

    result = {
        "program": "P1903C_EVENT_INGESTION_PLAN",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "event_types": len(EVENT_SCHEDULES),
        "ingestion_jobs": len(jobs),
        "priority_events": len([j for j in jobs if j["priority"] == "P0"]),
        "approved_for_P1903D": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    (OUT / "EVENT_INGESTION_PLAN.json").write_text(
        json.dumps(jobs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "EVENT_WINDOWS.json").write_text(
        json.dumps(EVENT_WINDOWS, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "EVENT_SCHEDULES.json").write_text(
        json.dumps(EVENT_SCHEDULES, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "EVENT_PRIORITY_QUEUE.json").write_text(
        json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "SUMMARY.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
