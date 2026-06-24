import ast, os, json, re
from pathlib import Path
from collections import defaultdict, deque

ROOT = Path(".").resolve()
APP = ROOT / "app"
OUT = Path(os.environ.get("RUNTIME_REACHABILITY_EVID", "_evidence/runtime_reachability_latest"))
OUT.mkdir(parents=True, exist_ok=True)

EXCLUDE = {"__pycache__", ".venv", "venv", "_evidence", "_backup", "_quarantine", ".git"}

def keep(path: Path):
    parts = set(path.parts)
    return not any(x in parts for x in EXCLUDE) and path.suffix == ".py"

files = [p for p in APP.rglob("*.py") if keep(p)]

modules = {}
imports = defaultdict(set)
functions = defaultdict(list)
calls = defaultdict(set)
classes = defaultdict(list)
errors = []

def modname(path: Path):
    rel = path.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)

for p in files:
    m = modname(p)
    modules[m] = str(p)
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception as e:
        errors.append({"file": str(p), "error": str(e)})
        continue

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports[m].add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports[m].add(node.module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[m].append({
                "name": node.name,
                "line": node.lineno,
                "returns": any(isinstance(x, ast.Return) for x in ast.walk(node)),
            })
        elif isinstance(node, ast.ClassDef):
            classes[m].append({"name": node.name, "line": node.lineno})
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name:
                calls[m].add(name)

# reachable modules by import graph
entrypoints = ["app.main", "app.main_core", "app.api.whatsapp"]
reachable = set()
q = deque([e for e in entrypoints if e in modules])

while q:
    cur = q.popleft()
    if cur in reachable:
        continue
    reachable.add(cur)
    for imp in imports.get(cur, []):
        candidates = []
        if imp in modules:
            candidates.append(imp)
        for m in modules:
            if m == imp or m.startswith(imp + "."):
                candidates.append(m)
        for c in candidates:
            if c not in reachable:
                q.append(c)

unreachable_modules = sorted(set(modules) - reachable)

# function reachability approximate: function name called anywhere
all_called_names = set()
for cset in calls.values():
    all_called_names |= cset

function_inventory = []
unused_functions = []
for m, flist in functions.items():
    for f in flist:
        item = {
            "module": m,
            "file": modules[m],
            "function": f["name"],
            "line": f["line"],
            "module_reachable": m in reachable,
            "name_called_somewhere": f["name"] in all_called_names,
            "returns": f["returns"],
        }
        function_inventory.append(item)
        if (m in reachable) and not item["name_called_somewhere"] and not f["name"].startswith("_"):
            unused_functions.append(item)

# duplicate module/function names
by_file_stem = defaultdict(list)
for m, p in modules.items():
    by_file_stem[Path(p).stem].append(m)

duplicate_module_stems = {k:v for k,v in by_file_stem.items() if len(v) > 1}

by_func = defaultdict(list)
for item in function_inventory:
    by_func[item["function"]].append(item["module"])
duplicate_functions = {k:v for k,v in by_func.items() if len(v) > 1 and not k.startswith("_")}

# potential response authorities
response_authorities = []
patterns = re.compile(r'return\s+["\']|return\s+f["\']|return\s+Response|return\s+_p19|return\s+universal|return\s+guard|return\s+twiml', re.I)
for p in files:
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    except:
        continue
    for i, line in enumerate(lines, 1):
        if patterns.search(line):
            response_authorities.append({"file": str(p), "line": i, "code": line.strip()})

# artifacts references: common missing file risks
artifact_refs = []
string_pat = re.compile(r'["\']([^"\']+\.(json|csv|txt|yaml|yml|db|sqlite|pkl))["\']', re.I)
for p in files:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    for match in string_pat.finditer(txt):
        ref = match.group(1)
        if ref.startswith("http"):
            continue
        rp = (ROOT / ref).resolve()
        artifact_refs.append({
            "file": str(p),
            "ref": ref,
            "exists_from_root": rp.exists()
        })

missing_artifacts = [x for x in artifact_refs if not x["exists_from_root"]]

summary = {
    "total_py_files_app": len(files),
    "total_modules": len(modules),
    "reachable_modules": len(reachable),
    "unreachable_modules": len(unreachable_modules),
    "runtime_coverage_percent": round((len(reachable) / max(1, len(modules))) * 100, 2),
    "total_functions": len(function_inventory),
    "potential_unused_public_functions_in_reachable_modules": len(unused_functions),
    "duplicate_module_stems": len(duplicate_module_stems),
    "duplicate_function_names": len(duplicate_functions),
    "response_authority_points": len(response_authorities),
    "missing_artifact_refs": len(missing_artifacts),
    "parse_errors": len(errors),
    "entrypoints": entrypoints,
}

def write_json(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

write_json("00_summary.json", summary)
write_json("01_modules.json", modules)
write_json("02_reachable_modules.json", sorted(reachable))
write_json("03_unreachable_modules.json", unreachable_modules)
write_json("04_function_inventory.json", function_inventory)
write_json("05_unused_public_functions_reachable.json", unused_functions)
write_json("06_duplicate_module_stems.json", duplicate_module_stems)
write_json("07_duplicate_function_names.json", duplicate_functions)
write_json("08_response_authority_points.json", response_authorities)
write_json("09_missing_artifact_refs.json", missing_artifacts)
write_json("10_import_graph.json", {k: sorted(v) for k,v in imports.items()})
write_json("11_parse_errors.json", errors)

report = f"""# Runtime Reachability Audit

## Summary
{json.dumps(summary, ensure_ascii=False, indent=2)}

## Conclusion
This audit estimates runtime reachability from FastAPI entrypoints and detects unreachable modules, duplicate modules/functions, response-authority points, missing artifact references, and parse errors.

## Next
1. Review unreachable modules.
2. Review response-authority points.
3. Reduce multiple response authorities into sovereign orchestrator.
4. Convert legacy modules into auxiliary providers.
"""
(OUT / "REPORT.md").write_text(report, encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
print("EVIDENCE=", str(OUT))
