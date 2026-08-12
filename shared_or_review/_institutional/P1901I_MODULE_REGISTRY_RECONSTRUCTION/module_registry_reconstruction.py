from __future__ import annotations

import json
import hashlib
from pathlib import Path
from collections import defaultdict


BASE = Path("_evidence/P1901H")
OUT = Path("_evidence/P1901I")

CATEGORY_WEIGHTS = {
    "execution_safety": 0.95,
    "memory": 0.72,
    "graph": 0.70,
    "learning": 0.66,
    "backtest": 0.68,
    "data": 0.62,
    "risk": 0.74,
    "portfolio": 0.55,
    "regime": 0.50,
}

MATURITY_RULES = [
    (85, "INSTITUTIONAL"),
    (70, "ADVANCED"),
    (50, "INTERMEDIATE"),
    (30, "PROTOTYPE"),
    (0, "TOY"),
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def cap_id(category: str, file: str, functions: list[str]) -> str:
    raw = f"{category}|{file}|{'|'.join(functions[:10])}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def infer_owner_module(file: str) -> str:
    parts = file.replace("\\", "/").split("/")

    for p in parts:
        low = p.lower()
        if low.startswith("p") and any(ch.isdigit() for ch in low):
            return p

    if "app" in parts:
        idx = parts.index("app")
        if idx + 1 < len(parts):
            return parts[idx + 1]

    if "reports" in parts:
        idx = parts.index("reports")
        if idx + 1 < len(parts):
            return parts[idx + 1]

    return parts[0] if parts else "unknown"


def infer_type(file: str, functions: list[str]) -> str:
    blob = " ".join([file] + functions).lower()

    if "registry" in blob:
        return "registry"
    if "runtime" in blob or "orchestrator" in blob or "run" in functions:
        return "runtime"
    if "engine" in blob:
        return "engine"
    if "backtest" in blob:
        return "backtest"
    if "memory" in blob:
        return "memory"
    if "graph" in blob:
        return "graph"
    if "portfolio" in blob or "allocation" in blob:
        return "portfolio"
    if "test" in blob:
        return "test"
    return "module"


def score_capability(category: str, item: dict) -> int:
    lines = item.get("lines", 0)
    functions = item.get("functions", [])
    classes = item.get("classes", [])
    live_hits = item.get("live_risk_hits", 0)

    density = min(lines / 500, 1.0) * 30
    function_depth = min(len(functions) / 10, 1.0) * 25
    class_depth = min(len(classes) / 3, 1.0) * 10
    category_bonus = CATEGORY_WEIGHTS.get(category, 0.5) * 25
    safety_penalty = min(live_hits * 5, 20)

    score = density + function_depth + class_depth + category_bonus + 10 - safety_penalty
    return int(max(0, min(100, round(score))))


def maturity(score: int) -> str:
    for threshold, label in MATURITY_RULES:
        if score >= threshold:
            return label
    return "TOY"


def build_master_registry():
    OUT.mkdir(parents=True, exist_ok=True)

    capability_map = read_json(BASE / "CAPABILITY_MAP.json")
    service_map = read_json(BASE / "SERVICE_MAP.json")
    dependency_graph = read_json(BASE / "DEPENDENCY_GRAPH.json")
    runtime_graph = read_json(BASE / "RUNTIME_GRAPH.json")
    registry_map = read_json(BASE / "CAPABILITY_REGISTRY.json")

    dependencies_by_file = defaultdict(list)
    for edge in dependency_graph.get("edges", []):
        dependencies_by_file[edge["source"]].append(edge["target"])

    capabilities = []

    for category, items in capability_map.get("capabilities", {}).items():
        for item in items:
            file = item["file"]
            functions = item.get("functions", [])
            score = score_capability(category, item)

            capabilities.append({
                "capability_id": cap_id(category, file, functions),
                "category": category,
                "type": infer_type(file, functions),
                "file": file,
                "owner_module": infer_owner_module(file),
                "functions": functions,
                "classes": item.get("classes", []),
                "lines": item.get("lines", 0),
                "dependencies": sorted(set(dependencies_by_file.get(file, []))),
                "live_risk_hits": item.get("live_risk_hits", 0),
                "institutional_score": score,
                "maturity": maturity(score),
                "status": "DISCOVERED",
            })

    by_category = defaultdict(list)
    by_owner = defaultdict(list)
    by_maturity = defaultdict(int)

    for c in capabilities:
        by_category[c["category"]].append(c["capability_id"])
        by_owner[c["owner_module"]].append(c["capability_id"])
        by_maturity[c["maturity"]] += 1

    master = {
        "program": "P1901I_MODULE_REGISTRY_RECONSTRUCTION",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "source": "P1901H_REAL_CAPABILITY_DISCOVERY",
        "capability_total": len(capabilities),
        "service_total": service_map.get("service_count", 0),
        "runtime_total": runtime_graph.get("runtime_node_count", 0),
        "registry_total": registry_map.get("registry_count", 0),
        "dependency_nodes": dependency_graph.get("node_count", 0),
        "dependency_edges": dependency_graph.get("edge_count", 0),
        "by_category": {k: len(v) for k, v in sorted(by_category.items())},
        "by_owner_module": {k: len(v) for k, v in sorted(by_owner.items())},
        "by_maturity": dict(sorted(by_maturity.items())),
        "institutional_readiness_score": round(
            sum(c["institutional_score"] for c in capabilities) / max(len(capabilities), 1),
            2
        ),
        "approved_for_P1901J": len(capabilities) > 0,
        "capabilities": sorted(
            capabilities,
            key=lambda x: (x["category"], x["owner_module"], x["file"])
        ),
    }

    (OUT / "MASTER_REGISTRY.json").write_text(
        json.dumps(master, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    compact = {
        "program": master["program"],
        "status": master["status"],
        "mode": master["mode"],
        "capability_total": master["capability_total"],
        "service_total": master["service_total"],
        "runtime_total": master["runtime_total"],
        "registry_total": master["registry_total"],
        "institutional_readiness_score": master["institutional_readiness_score"],
        "by_category": master["by_category"],
        "by_maturity": master["by_maturity"],
        "approved_for_P1901J": master["approved_for_P1901J"],
        "report": "_evidence/P1901I/MASTER_REGISTRY.json",
    }

    (OUT / "SUMMARY.json").write_text(
        json.dumps(compact, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return compact


if __name__ == "__main__":
    print(json.dumps(build_master_registry(), indent=2, ensure_ascii=False))
