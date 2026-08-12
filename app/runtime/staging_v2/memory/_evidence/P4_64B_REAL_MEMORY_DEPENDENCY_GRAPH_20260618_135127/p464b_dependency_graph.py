import ast
import json
from pathlib import Path
from collections import defaultdict, deque

ROOT = Path(".").resolve()
APP = ROOT / "app"

memory_keywords = [
    "memory",
    "graph",
    "semantic",
    "retrieval",
    "social",
    "emotion",
    "relationship",
    "longitudinal",
    "persona_continuity",
    "short_memory",
    "decision_memory",
]

entrypoints = [
    "app.runtime.cognitive_pipeline",
    "app.api.whatsapp",
]

def py_to_module(path: Path):
    rel = path.with_suffix("").relative_to(ROOT)
    return ".".join(rel.parts)

def module_to_py(module: str):
    return ROOT / (module.replace(".", "/") + ".py")

files = [p for p in APP.rglob("*.py") if "__pycache__" not in str(p)]

module_by_file = {}
source_by_module = {}
tree_by_module = {}

for p in files:
    try:
        mod = py_to_module(p)
        src = p.read_text(encoding="utf-8")
        tree = ast.parse(src)
        module_by_file[str(p)] = mod
        source_by_module[mod] = src
        tree_by_module[mod] = tree
    except Exception:
        pass

memory_modules = sorted([
    mod for mod in source_by_module
    if any(k in mod.lower() for k in memory_keywords)
])

imports = defaultdict(set)
calls = defaultdict(set)
functions = defaultdict(set)

for mod, tree in tree_by_module.items():
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app."):
                    imports[mod].add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("app."):
                imports[mod].add(node.module)
                for alias in node.names:
                    imports[mod].add(node.module + "." + alias.name)
        elif isinstance(node, ast.FunctionDef):
            functions[mod].add(node.name)
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                calls[mod].add(fn.id)
            elif isinstance(fn, ast.Attribute):
                calls[mod].add(fn.attr)

# reverse imports
imported_by = defaultdict(set)
for m, deps in imports.items():
    for d in deps:
        imported_by[d].add(m)
        base = ".".join(d.split(".")[:-1])
        if base:
            imported_by[base].add(m)

def reachable_from(start_mods):
    seen = set()
    q = deque(start_mods)
    while q:
        m = q.popleft()
        if m in seen:
            continue
        seen.add(m)

        for dep in imports.get(m, []):
            # normalize symbol import to real module if needed
            candidates = [dep]
            parts = dep.split(".")
            while len(parts) > 2:
                candidates.append(".".join(parts[:-1]))
                parts = parts[:-1]

            for c in candidates:
                if c in source_by_module and c not in seen:
                    q.append(c)
                    break

    return seen

pipeline_reachable = reachable_from(["app.runtime.cognitive_pipeline"])
whatsapp_reachable = reachable_from(["app.api.whatsapp"])

classification = {}

for mem in memory_modules:
    active_in_pipeline = mem in pipeline_reachable
    active_in_whatsapp = mem in whatsapp_reachable
    used_by_any = bool(imported_by.get(mem))

    if active_in_pipeline:
        cls = "ACTIVE_IN_PIPELINE"
    elif active_in_whatsapp:
        cls = "ACTIVE_IN_WHATSAPP_ADAPTER"
    elif used_by_any:
        cls = "ACTIVE_OUTSIDE_PIPELINE"
    else:
        cls = "ORPHANED_OR_UNUSED"

    classification[mem] = {
        "classification": cls,
        "active_in_pipeline": active_in_pipeline,
        "active_in_whatsapp": active_in_whatsapp,
        "imported_by": sorted(imported_by.get(mem, [])),
        "imports": sorted(imports.get(mem, [])),
        "functions": sorted(functions.get(mem, [])),
        "calls": sorted(calls.get(mem, [])),
    }

report = {
    "entrypoints": entrypoints,
    "memory_modules_count": len(memory_modules),
    "pipeline_reachable_count": len(pipeline_reachable),
    "whatsapp_reachable_count": len(whatsapp_reachable),
    "memory_modules": memory_modules,
    "pipeline_reachable": sorted(pipeline_reachable),
    "whatsapp_reachable": sorted(whatsapp_reachable),
    "classification": classification,
}

print(json.dumps(report, ensure_ascii=False, indent=2, default=str))

# CSV-like summary
print("\n" + "=" * 90)
print("CLASSIFICATION_SUMMARY")
print("=" * 90)

buckets = defaultdict(list)
for mem, data in classification.items():
    buckets[data["classification"]].append(mem)

for bucket in [
    "ACTIVE_IN_PIPELINE",
    "ACTIVE_IN_WHATSAPP_ADAPTER",
    "ACTIVE_OUTSIDE_PIPELINE",
    "ORPHANED_OR_UNUSED",
]:
    print("\n" + bucket)
    for m in sorted(buckets.get(bucket, [])):
        print("-", m)

print("\nP4.64B_COMPLETE")
