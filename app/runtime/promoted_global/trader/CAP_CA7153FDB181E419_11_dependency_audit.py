from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

ROOT = Path(".")
APP = ROOT / "app"
TESTS = ROOT / "tests"

EVID = Path(r"_evidence\\P19P36B_RUNTIME_DEPENDENCY_GRAPH_20260621_222624")

ENTRYPOINT_HINTS = [
    "app/main.py",
    "app/api/whatsapp.py",
    "app/companionship/p19p31_p19p36_companion_runtime.py",
    "app/context_runtime/universal_domain_context.py",
    "app/domains/universal_domain_router.py",
    "app/domains/fitness_runtime.py",
]

CAPABILITY_KEYWORDS = {
    "memory": ["memory", "memoria", "memória", "context", "profile", "store", "recall"],
    "emotion": ["emotion", "sentiment", "humanization", "care", "presence", "relationship"],
    "conversation": ["whatsapp", "conversation", "followup", "reply", "runtime", "router"],
    "retrieval": ["retrieval", "semantic", "embedding", "knowledge", "vector"],
    "planning": ["planner", "orchestrator", "task", "capability"],
    "trader": ["ftmo", "trader", "broker", "portfolio", "paper", "backtest"],
    "drive": ["drive", "ingestion", "file", "processor"],
    "governance": ["audit", "ledger", "governance", "guard", "validation"],
}

def module_name(path: Path) -> str:
    rel = path.as_posix()
    return rel[:-3].replace("/", ".")

def file_for_module(mod: str) -> str | None:
    p = Path(mod.replace(".", "/") + ".py")
    if p.exists():
        return p.as_posix()
    pkg = Path(mod.replace(".", "/")) / "__init__.py"
    if pkg.exists():
        return pkg.as_posix()
    return None

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def parse_imports(path: Path):
    txt = safe_read(path)
    imports = []
    try:
        tree = ast.parse(txt)
    except Exception as e:
        return imports, str(e)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.startswith("app."):
                    imports.append(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                imports.append(node.module)
    return imports, None

def parse_defs(path: Path):
    txt = safe_read(path)
    defs = []
    calls = []
    try:
        tree = ast.parse(txt)
    except Exception:
        return defs, calls

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs.append({
                "name": node.name,
                "type": type(node).__name__,
                "line": getattr(node, "lineno", None)
            })
        elif isinstance(node, ast.Call):
            fn = node.func
            name = None
            if isinstance(fn, ast.Name):
                name = fn.id
            elif isinstance(fn, ast.Attribute):
                name = fn.attr
            if name:
                calls.append({
                    "name": name,
                    "line": getattr(node, "lineno", None)
                })
    return defs, calls

def classify(path: Path, text: str):
    low = (path.as_posix() + "\n" + text[:5000]).lower()
    hits = {}
    for cap, keys in CAPABILITY_KEYWORDS.items():
        score = sum(1 for k in keys if k in low)
        if score:
            hits[cap] = score
    if not hits:
        return ["unknown"]
    return [k for k, _ in sorted(hits.items(), key=lambda x: -x[1])[:4]]

py_files = sorted([p for p in APP.rglob("*.py") if ".venv" not in p.parts])
test_files = sorted([p for p in TESTS.rglob("*.py")]) if TESTS.exists() else []

nodes = {}
edges = []
parse_errors = []

for p in py_files:
    txt = safe_read(p)
    mod = module_name(p)
    imports, err = parse_imports(p)
    defs, calls = parse_defs(p)

    if err:
        parse_errors.append({"path": p.as_posix(), "error": err})

    nodes[p.as_posix()] = {
        "module": mod,
        "path": p.as_posix(),
        "lines": txt.count("\n") + 1,
        "size": p.stat().st_size,
        "capabilities": classify(p, txt),
        "defs": defs[:80],
        "calls": calls[:120],
        "imports": imports,
        "is_entrypoint_hint": p.as_posix() in ENTRYPOINT_HINTS,
    }

    for imp in imports:
        target_file = file_for_module(imp)
        edges.append({
            "source": p.as_posix(),
            "import": imp,
            "target": target_file,
            "edge_type": "import"
        })

# references by text/name
all_text = "\n".join([safe_read(p) for p in py_files + test_files])
module_refs = {}
for p in py_files:
    mod = module_name(p)
    base = p.stem
    count_mod = len(re.findall(re.escape(mod), all_text))
    count_base = len(re.findall(r"\b" + re.escape(base) + r"\b", all_text))
    module_refs[p.as_posix()] = {
        "module_ref_count": count_mod,
        "basename_ref_count": count_base
    }

incoming = defaultdict(int)
outgoing = defaultdict(int)
for e in edges:
    outgoing[e["source"]] += 1
    if e["target"]:
        incoming[e["target"]] += 1

entrypoints = []
for p, n in nodes.items():
    if n["is_entrypoint_hint"] or p.endswith("/main.py") or "webhook" in p or "whatsapp" in p:
        entrypoints.append(p)

dead_candidates = []
for p, n in nodes.items():
    refs = module_refs[p]
    is_tested = any(p.replace("app/", "").replace("/", "_").replace(".py", "") in tf.as_posix() for tf in test_files)
    if (
        incoming[p] == 0
        and outgoing[p] == 0
        and not n["is_entrypoint_hint"]
        and refs["basename_ref_count"] <= 1
        and not is_tested
    ):
        dead_candidates.append({
            "path": p,
            "reason": "no incoming imports, no outgoing imports, no obvious text refs",
            "capabilities": n["capabilities"]
        })

duplicate_groups = defaultdict(list)
for p, n in nodes.items():
    key = "|".join(sorted(n["capabilities"]))
    duplicate_groups[key].append(p)

duplicates = []
for cap_key, paths in duplicate_groups.items():
    if cap_key != "unknown" and len(paths) >= 2:
        duplicates.append({
            "capability_group": cap_key,
            "count": len(paths),
            "paths": paths[:80]
        })

runtime_entry_paths = {
    "entrypoints": entrypoints,
    "known_certified_runtime": ENTRYPOINT_HINTS,
    "whatsapp_execution_core": [
        "app/main.py",
        "app/api/whatsapp.py",
        "app/context_runtime/universal_domain_context.py",
        "app/domains/universal_domain_router.py",
        "app/domains/fitness_runtime.py",
        "app/companionship/p19p31_p19p36_companion_runtime.py",
    ],
}

summary = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "python_files": len(py_files),
    "test_files": len(test_files),
    "nodes": len(nodes),
    "edges": len(edges),
    "parse_errors": len(parse_errors),
    "dead_candidates": len(dead_candidates),
    "duplicate_groups": len(duplicates),
    "entrypoints": len(entrypoints),
    "top_capabilities": Counter(c for n in nodes.values() for c in n["capabilities"]).most_common(),
}

outputs = {
    "runtime_dependency_graph.json": {"summary": summary, "nodes": nodes, "edges": edges},
    "runtime_entrypoints.json": runtime_entry_paths,
    "runtime_dead_modules.json": dead_candidates,
    "runtime_duplicate_modules.json": duplicates,
    "runtime_parse_errors.json": parse_errors,
    "runtime_module_reference_counts.json": module_refs,
    "runtime_dependency_summary.json": summary,
}

EVID.mkdir(parents=True, exist_ok=True)
for name, data in outputs.items():
    (EVID / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
