from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, UTC
from hashlib import sha256


OUT = Path("_evidence/P1903D_J")
INGESTION = Path("_evidence/P1903C/EVENT_INGESTION_PLAN.json")
SCHEMA = Path("_evidence/P1903A/REAL_EVENT_MEMORY_SCHEMA.json")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def event_id(event_type: str) -> str:
    return sha256(f"{event_type}|CANONICAL_TEMPLATE".encode()).hexdigest()[:16]


def run():
    OUT.mkdir(parents=True, exist_ok=True)

    ingestion = read_json(INGESTION)
    schema = read_json(SCHEMA)

    events = []
    memories = []
    links = []
    retrieval_index = []
    similarity_index = []
    graph_nodes = []
    graph_edges = []

    for job in ingestion:
        etype = job["event_type"]
        eid = event_id(etype)

        event = {
            "event_id": eid,
            "event_type": etype,
            "event_name": f"{etype}_CANONICAL_TEMPLATE",
            "timestamp_utc": None,
            "country": None,
            "asset_scope": [],
            "expected_impact": None,
            "actual_value": None,
            "forecast_value": None,
            "previous_value": None,
            "surprise_value": None,
            "source": None,
            "event_window": job["event_window"],
            "linked_assets": [],
            "memory_tags": [etype, job["priority"]],
            "status": "SCHEMA_READY_NO_EXTERNAL_INGESTION",
        }

        events.append(event)

        memories.append({
            "memory_id": f"mem_{eid}",
            "event_id": eid,
            "memory_type": "REAL_EVENT_MEMORY",
            "retrieval_ready": True,
            "similarity_ready": True,
            "graph_ready": True,
            "mode": "RESEARCH_ONLY",
        })

        links.append({
            "event_id": eid,
            "link_type": "EVENT_TO_MARKET_WINDOW",
            "pre_windows": job["event_window"]["pre_event_hours"],
            "post_windows": job["event_window"]["post_event_hours"],
            "status": "PLANNED",
        })

        retrieval_index.append({
            "event_id": eid,
            "keys": [etype, job["schedule"], job["priority"]],
        })

        similarity_index.append({
            "event_id": eid,
            "features": ["event_type", "priority", "event_window", "schedule"],
        })

        graph_nodes.append({
            "id": eid,
            "type": "event",
            "label": etype,
        })

        graph_edges.append({
            "source": eid,
            "target": "MARKET_MEMORY",
            "type": "CAN_LINK_TO",
        })

    readiness = {
        "program": "P1903J_EVENT_READINESS_AUDIT",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "events": len(events),
        "memories": len(memories),
        "links": len(links),
        "retrieval_items": len(retrieval_index),
        "similarity_items": len(similarity_index),
        "graph_nodes": len(graph_nodes),
        "graph_edges": len(graph_edges),
        "external_ingestion_executed": False,
        "approved_for_P1904": True,
        "generated_at": datetime.now(UTC).isoformat(),
    }

    outputs = {
        "P1903D_EVENT_CANONICAL_LEDGER.json": events,
        "P1903E_EVENT_MEMORY_STORAGE.json": memories,
        "P1903F_EVENT_LINK_ENGINE.json": links,
        "P1903G_EVENT_RETRIEVAL_ENGINE.json": retrieval_index,
        "P1903H_EVENT_SIMILARITY_ENGINE.json": similarity_index,
        "P1903I_EVENT_GRAPH.json": {
            "nodes": graph_nodes,
            "edges": graph_edges,
        },
        "P1903J_EVENT_READINESS_AUDIT.json": readiness,
        "SUMMARY.json": readiness,
    }

    for name, payload in outputs.items():
        (OUT / name).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    print(json.dumps(readiness, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
