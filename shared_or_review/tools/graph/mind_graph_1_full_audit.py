import ast
import json
import os
import re
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core")
OUT = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\MIND-GRAPH-1_FULL_RUNTIME_TREE_AUDIT_20260625_152120")

SCAN_DIRS = ["app", "services", "tools"]
PY_FILES = []

for d in SCAN_DIRS:
    base = ROOT / d
    if base.exists():
        PY_FILES.extend(base.rglob("*.py"))

def rel(p):
    return str(p.relative_to(ROOT)).replace("\\", "/")

nodes = {}
edges = []
routes = []
imports_map = defaultdict(list)
reverse_imports = defaultdict(list)
function_defs = defaultdict(list)
class_defs = defaultdict(list)
function_calls = defaultdict(list)
errors = []

for path in PY_FILES:
    r = rel(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    node = {
        "file": r,
        "lines": len(lines),
        "size_bytes": path.stat().st_size,
        "imports": [],
        "from_imports": [],
        "functions": [],
        "classes": [],
        "routes": [],
        "calls": [],
        "has_fastapi": "FastAPI" in text or "APIRouter" in text,
        "has_response": "Response(" in text,
        "has_twiML": "twiml" in text.lower(),
        "has_runtime": "runtime" in r.lower() or "runtime" in text.lower(),
        "has_test": "test" in r.lower() or "pytest" in text.lower(),
    }

    try:
        tree = ast.parse(text)
    except Exception as exc:
        errors.append({"file": r, "error": type(exc).__name__, "message": str(exc)})
        nodes[r] = node
        continue

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                node["imports"].append(a.name)
        elif isinstance(n, ast.ImportFrom):
            mod = n.module or ""
            node["from_imports"].append(mod)
        elif isinstance(n, ast.FunctionDef):
            node["functions"].append({"name": n.name, "line": n.lineno, "end": getattr(n, "end_lineno", n.lineno)})
            function_defs[r].append(n.name)
        elif isinstance(n, ast.ClassDef):
            node["classes"].append({"name": n.name, "line": n.lineno, "end": getattr(n, "end_lineno", n.lineno)})
            class_defs[r].append(n.name)
        elif isinstance(n, ast.Call):
            cname = None
            if isinstance(n.func, ast.Name):
                cname = n.func.id
            elif isinstance(n.func, ast.Attribute):
                cname = n.func.attr
            if cname:
                node["calls"].append({"name": cname, "line": getattr(n, "lineno", None)})
                function_calls[r].append(cname)

        # FastAPI decorators
        if isinstance(n, ast.FunctionDef):
            for dec in n.decorator_list:
                txt = ast.unparse(dec) if hasattr(ast, "unparse") else ""
                if any(x in txt for x in [".get(", ".post(", ".put(", ".delete(", ".patch("]):
                    node["routes"].append({"function": n.name, "line": n.lineno, "decorator": txt})
                    routes.append({"file": r, "function": n.name, "line": n.lineno, "decorator": txt})

    nodes[r] = node

# Resolve internal import edges
all_files = set(nodes.keys())

def mod_to_path(mod):
    if not mod:
        return None
    parts = mod.split(".")
    candidates = [
        "/".join(parts) + ".py",
        "/".join(parts) + "/__init__.py",
    ]
    for c in candidates:
        if c in all_files:
            return c
    return None

for file, node in nodes.items():
    for mod in node["imports"] + node["from_imports"]:
        target = mod_to_path(mod)
        if target:
            edges.append({"source": file, "target": target, "type": "import"})
            imports_map[file].append(target)
            reverse_imports[target].append(file)

# Call edges by function name across files
func_to_files = defaultdict(list)
for f, funcs in function_defs.items():
    for name in funcs:
        func_to_files[name].append(f)

for src, calls in function_calls.items():
    for call in calls:
        targets = func_to_files.get(call, [])
        for tgt in targets:
            if tgt != src:
                edges.append({"source": src, "target": tgt, "type": "call_name", "symbol": call})

# Entry points
entry_files = set()
for r in routes:
    entry_files.add(r["file"])

for f in nodes:
    low = f.lower()
    if low.endswith("main.py") or "whatsapp.py" in low or "runpod" in low or "routes" in low:
        entry_files.add(f)

# Reachability
adj = defaultdict(list)
for e in edges:
    adj[e["source"]].append(e["target"])

reachable = set()
q = deque(entry_files)
while q:
    cur = q.popleft()
    if cur in reachable:
        continue
    reachable.add(cur)
    for nxt in adj[cur]:
        if nxt not in reachable:
            q.append(nxt)

orphans = sorted(all_files - reachable)

# Centrality simple
in_degree = defaultdict(int)
out_degree = defaultdict(int)
for e in edges:
    out_degree[e["source"]] += 1
    in_degree[e["target"]] += 1

ranked_nodes = []
for f in sorted(all_files):
    ranked_nodes.append({
        "file": f,
        "in_degree": in_degree[f],
        "out_degree": out_degree[f],
        "degree": in_degree[f] + out_degree[f],
        "reachable": f in reachable,
        "lines": nodes[f]["lines"],
        "functions": len(nodes[f]["functions"]),
        "classes": len(nodes[f]["classes"]),
        "routes": len(nodes[f]["routes"]),
    })

ranked_nodes.sort(key=lambda x: x["degree"], reverse=True)

summary = {
    "mission": "MIND-GRAPH-1",
    "root": str(ROOT),
    "python_files": len(PY_FILES),
    "nodes": len(nodes),
    "edges": len(edges),
    "routes": len(routes),
    "entry_files": len(entry_files),
    "reachable": len(reachable),
    "orphans": len(orphans),
    "parse_errors": len(errors),
    "top_degree_file": ranked_nodes[0]["file"] if ranked_nodes else None,
}

out = {
    "summary": summary,
    "entry_files": sorted(entry_files),
    "routes": routes,
    "nodes_ranked": ranked_nodes,
    "orphans": orphans,
    "edges": edges,
    "parse_errors": errors,
}

(OUT / "mind_graph_full_audit.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

# CSV edges
with (OUT / "mind_graph_edges.csv").open("w", encoding="utf-8") as f:
    f.write("source,target,type,symbol\n")
    for e in edges:
        f.write(f"{e.get('source','')},{e.get('target','')},{e.get('type','')},{e.get('symbol','')}\n")

# Markdown report
md = []
md.append("# MIND-GRAPH-1 Full Runtime Tree Audit\n")
md.append("## Summary\n")
for k, v in summary.items():
    md.append(f"- **{k}**: {v}")

md.append("\n## Entry Files\n")
for f in sorted(entry_files):
    md.append(f"- `{f}`")

md.append("\n## Routes\n")
for r in routes:
    md.append(f"- `{r['file']}` line {r['line']} `{r['function']}` => `{r['decorator']}`")

md.append("\n## Top 30 Central Nodes\n")
md.append("| file | degree | in | out | reachable | lines | funcs | classes | routes |")
md.append("|---|---:|---:|---:|---|---:|---:|---:|---:|")
for n in ranked_nodes[:30]:
    md.append(f"| `{n['file']}` | {n['degree']} | {n['in_degree']} | {n['out_degree']} | {n['reachable']} | {n['lines']} | {n['functions']} | {n['classes']} | {n['routes']} |")

md.append("\n## Orphans First 100\n")
for f in orphans[:100]:
    md.append(f"- `{f}`")

md.append("\n## Parse Errors\n")
for e in errors:
    md.append(f"- `{e['file']}` {e['error']}: {e['message']}")

(OUT / "MIND_GRAPH_1_REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, indent=2, ensure_ascii=False))

