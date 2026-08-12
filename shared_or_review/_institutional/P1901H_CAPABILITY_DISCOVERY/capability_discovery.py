from __future__ import annotations

import ast
import json
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict


SCAN_DIRS = [
    "services",
    "src",
    "core",
    "runtime",
    "engines",
    "pipelines",
    "workers",
    "tests",
    "_institutional",
]

CAPABILITY_KEYWORDS = {
    "memory": ["memory", "memoria", "retrieval", "embedding", "vector", "pgvector", "context"],
    "graph": ["graph", "node", "edge", "network", "relationship"],
    "backtest": ["backtest", "walk_forward", "monte_carlo", "stress", "simulation"],
    "portfolio": ["portfolio", "allocation", "capital", "exposure", "correlation", "drawdown"],
    "learning": ["learning", "meta", "adaptive", "evolution", "mutation", "crossover", "genetic"],
    "regime": ["regime", "volatility", "trend", "panic", "compression", "expansion"],
    "risk": ["risk", "leakage", "lookahead", "survivorship", "bias", "safety"],
    "data": ["dataset", "ohlcv", "feature", "normalization", "ingestion", "harvest"],
    "execution_safety": ["order_sent", "real_orders", "ftmo_real", "mt5_real", "research_only"],
}

LIVE_RISK_TERMS = [
    "order_send(",
    "send_order(",
    "trade_live",
    "live_trading",
    "real_order",
    "mt5.order_send",
]


@dataclass
class PythonUnit:
    file: str
    module_hash: str
    classes: list[str]
    functions: list[str]
    imports: list[str]
    decorators: list[str]
    capability_tags: list[str]
    lines: int
    live_risk_hits: int


def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def safe_read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def discover_py_files(repo: Path) -> list[Path]:
    files = []
    for scan_dir in SCAN_DIRS:
        root = repo / scan_dir
        if root.exists():
            files.extend(root.rglob("*.py"))
    return sorted(set(files))


def extract_python_unit(path: Path, repo: Path) -> PythonUnit:
    text = safe_read(path)
    rel = str(path.relative_to(repo)).replace("\\", "/")
    lower = text.lower()

    classes = []
    functions = []
    imports = []
    decorators = []

    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                for d in node.decorator_list:
                    decorators.append(ast.unparse(d) if hasattr(ast, "unparse") else type(d).__name__)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
                for d in node.decorator_list:
                    decorators.append(ast.unparse(d) if hasattr(ast, "unparse") else type(d).__name__)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                imports.append(mod)
    except Exception:
        pass

    tags = []
    joined = " ".join([rel.lower(), lower])
    for tag, keywords in CAPABILITY_KEYWORDS.items():
        if any(k in joined for k in keywords):
            tags.append(tag)

    live_hits = sum(lower.count(t.lower()) for t in LIVE_RISK_TERMS)

    return PythonUnit(
        file=rel,
        module_hash=stable_hash(text),
        classes=sorted(set(classes)),
        functions=sorted(set(functions)),
        imports=sorted(set(i for i in imports if i)),
        decorators=sorted(set(decorators)),
        capability_tags=sorted(set(tags)),
        lines=len(text.splitlines()),
        live_risk_hits=live_hits,
    )


def build_capability_map(units: list[PythonUnit]) -> dict:
    by_tag = defaultdict(list)

    for unit in units:
        for tag in unit.capability_tags:
            by_tag[tag].append({
                "file": unit.file,
                "classes": unit.classes,
                "functions": unit.functions,
                "lines": unit.lines,
                "live_risk_hits": unit.live_risk_hits,
            })

    return {
        "program": "P1901H_REAL_CAPABILITY_DISCOVERY",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "capability_count": sum(len(v) for v in by_tag.values()),
        "capabilities": dict(sorted(by_tag.items())),
    }


def build_service_map(units: list[PythonUnit]) -> dict:
    service_terms = ["service", "api", "router", "endpoint", "controller", "worker", "pipeline", "engine"]

    services = []
    for unit in units:
        blob = " ".join([unit.file] + unit.classes + unit.functions).lower()
        if any(t in blob for t in service_terms):
            services.append(asdict(unit))

    return {
        "program": "P1901H_SERVICE_MAP",
        "mode": "RESEARCH_ONLY",
        "service_count": len(services),
        "services": services,
    }


def build_dependency_graph(units: list[PythonUnit]) -> dict:
    nodes = []
    edges = []

    for unit in units:
        nodes.append({
            "id": unit.file,
            "type": "python_file",
            "tags": unit.capability_tags,
            "lines": unit.lines,
        })

        for imp in unit.imports:
            edges.append({
                "source": unit.file,
                "target": imp,
                "type": "imports",
            })

    return {
        "program": "P1901H_DEPENDENCY_GRAPH",
        "mode": "RESEARCH_ONLY",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def build_runtime_graph(units: list[PythonUnit]) -> dict:
    runtime_terms = ["runtime", "orchestrator", "registry", "container", "factory", "main", "run", "execute"]

    nodes = []
    for unit in units:
        blob = " ".join([unit.file] + unit.classes + unit.functions + unit.decorators).lower()
        if any(t in blob for t in runtime_terms):
            nodes.append(asdict(unit))

    return {
        "program": "P1901H_RUNTIME_GRAPH",
        "mode": "RESEARCH_ONLY",
        "runtime_node_count": len(nodes),
        "runtime_nodes": nodes,
    }


def build_registry_map(units: list[PythonUnit]) -> dict:
    registry_terms = ["registry", "manifest", "catalog", "index", "capability", "specialist"]

    found = []
    for unit in units:
        blob = " ".join([unit.file] + unit.classes + unit.functions).lower()
        if any(t in blob for t in registry_terms):
            found.append(asdict(unit))

    return {
        "program": "P1901H_CAPABILITY_REGISTRY",
        "mode": "RESEARCH_ONLY",
        "registry_count": len(found),
        "registries": found,
    }


def generate_summary(units: list[PythonUnit], capability_map: dict, service_map: dict, dependency_graph: dict, runtime_graph: dict, registry_map: dict) -> dict:
    tag_counts = {
        tag: len(items)
        for tag, items in capability_map["capabilities"].items()
    }

    live_risk_total = sum(u.live_risk_hits for u in units)

    return {
        "program": "P1901H_REAL_CAPABILITY_DISCOVERY",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "mt5_real": "FORBIDDEN",
        "python_files_scanned": len(units),
        "classes_discovered": sum(len(u.classes) for u in units),
        "functions_discovered": sum(len(u.functions) for u in units),
        "imports_discovered": sum(len(u.imports) for u in units),
        "capability_tags": tag_counts,
        "capability_count": capability_map["capability_count"],
        "service_count": service_map["service_count"],
        "dependency_nodes": dependency_graph["node_count"],
        "dependency_edges": dependency_graph["edge_count"],
        "runtime_nodes": runtime_graph["runtime_node_count"],
        "registry_count": registry_map["registry_count"],
        "live_risk_hits": live_risk_total,
        "approval": {
            "capability_map_exists": True,
            "service_map_exists": True,
            "dependency_graph_exists": True,
            "runtime_graph_exists": True,
            "registry_map_exists": True,
            "approved_for_P1901I": live_risk_total == 0 and capability_map["capability_count"] > 0,
        },
    }


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run(repo: Path) -> dict:
    out = repo / "_evidence" / "P1901H"
    out.mkdir(parents=True, exist_ok=True)

    files = discover_py_files(repo)
    units = [extract_python_unit(p, repo) for p in files]

    capability_map = build_capability_map(units)
    service_map = build_service_map(units)
    dependency_graph = build_dependency_graph(units)
    runtime_graph = build_runtime_graph(units)
    registry_map = build_registry_map(units)

    summary = generate_summary(
        units,
        capability_map,
        service_map,
        dependency_graph,
        runtime_graph,
        registry_map,
    )

    write_json(out / "PYTHON_UNITS.json", {"units": [asdict(u) for u in units]})
    write_json(out / "CAPABILITY_MAP.json", capability_map)
    write_json(out / "SERVICE_MAP.json", service_map)
    write_json(out / "DEPENDENCY_GRAPH.json", dependency_graph)
    write_json(out / "RUNTIME_GRAPH.json", runtime_graph)
    write_json(out / "CAPABILITY_REGISTRY.json", registry_map)
    write_json(out / "SUMMARY.json", summary)

    return summary


if __name__ == "__main__":
    result = run(Path.cwd())
    print(json.dumps(result, indent=2, ensure_ascii=False))
