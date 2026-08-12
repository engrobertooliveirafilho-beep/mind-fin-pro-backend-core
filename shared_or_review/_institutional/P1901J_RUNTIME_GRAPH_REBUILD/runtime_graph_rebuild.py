from __future__ import annotations

import json
from pathlib import Path
from collections import defaultdict, deque


IN = Path("_evidence/P1901I/MASTER_REGISTRY.json")
OUT = Path("_evidence/P1901J")


RUNTIME_TYPES = {"runtime", "engine", "registry"}
CRITICAL_CATEGORIES = {
    "execution_safety",
    "data",
    "backtest",
    "memory",
    "learning",
    "portfolio",
    "risk",
    "regime",
    "graph",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_dependency(dep: str) -> str:
    return dep.replace("\\", "/").strip()


def build_runtime_graph():
    OUT.mkdir(parents=True, exist_ok=True)

    registry = read_json(IN)
    caps = registry.get("capabilities", [])

    nodes = []
    edges = []

    file_to_caps = defaultdict(list)
    owner_to_caps = defaultdict(list)
    category_to_caps = defaultdict(list)

    for cap in caps:
        file_to_caps[cap["file"]].append(cap)
        owner_to_caps[cap["owner_module"]].append(cap)
        category_to_caps[cap["category"]].append(cap)

    for cap in caps:
        node_type = cap["type"]
        criticality = "CRITICAL" if cap["category"] in CRITICAL_CATEGORIES else "STANDARD"

        nodes.append({
            "id": cap["capability_id"],
            "file": cap["file"],
            "owner_module": cap["owner_module"],
            "category": cap["category"],
            "type": node_type,
            "maturity": cap["maturity"],
            "institutional_score": cap["institutional_score"],
            "criticality": criticality,
            "runtime_candidate": node_type in RUNTIME_TYPES or cap["category"] in CRITICAL_CATEGORIES,
        })

        for dep in cap.get("dependencies", []):
            dep_norm = normalize_dependency(dep)
            edges.append({
                "source": cap["capability_id"],
                "target": dep_norm,
                "type": "external_import",
                "weight": 1,
            })

    owner_edges = []
    for owner, owner_caps in owner_to_caps.items():
        if len(owner_caps) <= 1:
            continue
        root = sorted(owner_caps, key=lambda x: (-x["institutional_score"], x["file"]))[0]
        for cap in owner_caps:
            if cap["capability_id"] != root["capability_id"]:
                owner_edges.append({
                    "source": root["capability_id"],
                    "target": cap["capability_id"],
                    "type": "same_owner_runtime_relation",
                    "weight": 2,
                })

    category_edges = []
    for category, cat_caps in category_to_caps.items():
        if len(cat_caps) <= 1:
            continue
        root = sorted(cat_caps, key=lambda x: (-x["institutional_score"], x["file"]))[0]
        for cap in cat_caps:
            if cap["capability_id"] != root["capability_id"]:
                category_edges.append({
                    "source": root["capability_id"],
                    "target": cap["capability_id"],
                    "type": "same_category_relation",
                    "weight": 1,
                })

    edges.extend(owner_edges)
    edges.extend(category_edges)

    inbound = defaultdict(int)
    outbound = defaultdict(int)

    for edge in edges:
        outbound[edge["source"]] += 1
        inbound[edge["target"]] += 1

    node_index = {n["id"]: n for n in nodes}

    hubs = []
    orphans = []

    for n in nodes:
        deg = inbound[n["id"]] + outbound[n["id"]]
        n["inbound_degree"] = inbound[n["id"]]
        n["outbound_degree"] = outbound[n["id"]]
        n["total_degree"] = deg

        if deg >= 5:
            hubs.append(n)
        if deg == 0:
            orphans.append(n)

    weak_runtime_nodes = [
        n for n in nodes
        if n["runtime_candidate"] and n["institutional_score"] < 50
    ]

    category_coverage = {
        cat: len(items)
        for cat, items in sorted(category_to_caps.items())
    }

    institutional_bottlenecks = sorted(
        weak_runtime_nodes,
        key=lambda x: (x["institutional_score"], x["category"], x["file"])
    )[:50]

    graph = {
        "program": "P1901J_RUNTIME_GRAPH_REBUILD",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "source": "P1901I_MASTER_REGISTRY",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "hub_count": len(hubs),
        "orphan_count": len(orphans),
        "weak_runtime_node_count": len(weak_runtime_nodes),
        "category_coverage": category_coverage,
        "institutional_bottlenecks": institutional_bottlenecks,
        "approved_for_P1901K": len(nodes) > 0 and len(edges) > 0,
        "nodes": nodes,
        "edges": edges,
    }

    summary = {
        "program": graph["program"],
        "status": graph["status"],
        "mode": graph["mode"],
        "node_count": graph["node_count"],
        "edge_count": graph["edge_count"],
        "hub_count": graph["hub_count"],
        "orphan_count": graph["orphan_count"],
        "weak_runtime_node_count": graph["weak_runtime_node_count"],
        "category_coverage": graph["category_coverage"],
        "approved_for_P1901K": graph["approved_for_P1901K"],
        "report": "_evidence/P1901J/RUNTIME_GRAPH_V2.json",
    }

    (OUT / "RUNTIME_GRAPH_V2.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return summary


if __name__ == "__main__":
    print(json.dumps(build_runtime_graph(), indent=2, ensure_ascii=False))
