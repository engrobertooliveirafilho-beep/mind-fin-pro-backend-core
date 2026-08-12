from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC


OUT = Path("_evidence/P1903B")

SOURCES = {
    "FOMC": ["FED_OFFICIAL_CALENDAR", "FRED", "ECONOMIC_CALENDAR_EXPORT"],
    "CPI": ["BLS", "FRED", "ECONOMIC_CALENDAR_EXPORT"],
    "PPI": ["BLS", "FRED", "ECONOMIC_CALENDAR_EXPORT"],
    "NFP": ["BLS", "FRED", "ECONOMIC_CALENDAR_EXPORT"],
    "ECB": ["ECB_OFFICIAL_CALENDAR", "ECONOMIC_CALENDAR_EXPORT"],
    "BOJ": ["BOJ_OFFICIAL_CALENDAR", "ECONOMIC_CALENDAR_EXPORT"],
    "BOE": ["BOE_OFFICIAL_CALENDAR", "ECONOMIC_CALENDAR_EXPORT"],
    "FED_SPEECH": ["FED_SPEECH_CALENDAR", "ECONOMIC_CALENDAR_EXPORT"],
    "WAR": ["MANUAL_VERIFIED_EVENT_LEDGER", "NEWS_EVENT_LEDGER"],
    "PANDEMIC": ["WHO", "MANUAL_VERIFIED_EVENT_LEDGER"],
    "BANKING_CRISIS": ["FDIC", "FED", "MANUAL_VERIFIED_EVENT_LEDGER"],
    "ENERGY_SHOCK": ["EIA", "OPEC", "MANUAL_VERIFIED_EVENT_LEDGER"],
    "ELECTION": ["OFFICIAL_ELECTION_CALENDAR", "MANUAL_VERIFIED_EVENT_LEDGER"],
    "DEBT_CRISIS": ["IMF", "WORLD_BANK", "MANUAL_VERIFIED_EVENT_LEDGER"],
}

QUALITY = {
    "official": 95,
    "macro_database": 88,
    "economic_calendar": 76,
    "manual_verified": 82,
    "news_ledger": 65,
}


def classify_source(src: str) -> dict:
    s = src.lower()

    if "official" in s or src in {"BLS", "FED", "FDIC", "WHO", "EIA", "OPEC", "IMF", "WORLD_BANK", "ECB_OFFICIAL_CALENDAR", "BOJ_OFFICIAL_CALENDAR", "BOE_OFFICIAL_CALENDAR"}:
        return {"class": "official", "score": QUALITY["official"]}

    if src == "FRED":
        return {"class": "macro_database", "score": QUALITY["macro_database"]}

    if "ECONOMIC_CALENDAR" in src:
        return {"class": "economic_calendar", "score": QUALITY["economic_calendar"]}

    if "MANUAL_VERIFIED" in src:
        return {"class": "manual_verified", "score": QUALITY["manual_verified"]}

    return {"class": "news_ledger", "score": QUALITY["news_ledger"]}


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    registry = []
    for event_type, sources in SOURCES.items():
        for src in sources:
            meta = classify_source(src)
            registry.append({
                "event_type": event_type,
                "source": src,
                "source_class": meta["class"],
                "quality_score": meta["score"],
                "approved": meta["score"] >= 75,
                "mode": "RESEARCH_ONLY",
            })

    approved = [r for r in registry if r["approved"]]
    rejected = [r for r in registry if not r["approved"]]

    summary = {
        "program": "P1903B_EVENT_SOURCE_REGISTRY",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "event_type_count": len(SOURCES),
        "source_count": len(registry),
        "approved_sources": len(approved),
        "rejected_sources": len(rejected),
        "approved_for_P1903C": len(approved) > 0,
        "report": "_evidence/P1903B/EVENT_SOURCE_REGISTRY.json",
        "generated_at": datetime.now(UTC).isoformat(),
    }

    (OUT / "EVENT_SOURCE_REGISTRY.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
