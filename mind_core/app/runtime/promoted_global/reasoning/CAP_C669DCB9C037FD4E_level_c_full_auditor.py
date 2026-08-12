import os
import ast
import json
import hashlib
import importlib.util
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DIR = Path(os.environ.get("LEVEL_C_REPORT_DIR", ROOT / "evidence" / f"P4.51_LEVEL_C_FULL_AUDIT_{STAMP}" / "reports"))
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SCAN_DIRS = ["app", "services", "scripts", "tests"]
PY_FILES = []
for d in SCAN_DIRS:
    p = ROOT / d
    if p.exists():
        PY_FILES.extend([x for x in p.rglob("*.py") if "__pycache__" not in str(x)])

KEYWORDS = {
    "debug": ["debug", "trace", "verbose", "diagnostic", "diagnostics"],
    "legacy": ["legacy", "old", "v1", "deprecated", "obsolete"],
    "experimental": ["experimental", "prototype", "sandbox", "beta", "future", "research"],
    "shadow_only": ["shadow", "shadow_only"],
    "incomplete": ["todo", "fixme", "notimplemented", "pass #", "placeholder"],
    "hidden_capabilities": ["capability", "orchestrator", "planner", "simulation", "memory", "graph", "swarm", "agent", "adapter", "pipeline"],
}

CLASS_ORDER = ["BROKEN", "DEPRECATED", "SHADOW", "PARTIAL", "ORPHAN", "UNUSED", "ACTIVE"]

def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def safe_read(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def rel(path):
    return str(path.relative_to(ROOT)).replace("\\", "/")

def classify_file(path, text, imports_by_file, imported_modules, route_hits, test_hits):
    low = text.lower()
    name = path.stem.lower()
    tags = []

    for tag, words in KEYWORDS.items():
        if any(w in low or w in name for w in words):
            tags.append(tag)

    status = "UNUSED"

    if "deprecated" in tags or "obsolete" in low:
        status = "DEPRECATED"
    elif "shadow_only" in tags:
        status = "SHADOW"
    elif "notimplemented" in low or "raise notimplementederror" in low:
        status = "PARTIAL"
    elif rel(path) in test_hits or rel(path) in route_hits:
        status = "ACTIVE"
    elif path.stem in imported_modules:
        status = "ACTIVE"
    elif "experimental" in tags or "incomplete" in tags:
        status = "PARTIAL"
    else:
        status = "ORPHAN"

    if "syntax_error_detected" in tags:
        status = "BROKEN"

    return status, tags

def module_name_from_path(path):
    try:
        r = path.relative_to(ROOT).with_suffix("")
        return ".".join(r.parts)
    except Exception:
        return path.stem

all_text = {}
asts = {}
syntax_errors = {}

for f in PY_FILES:
    text = safe_read(f)
    all_text[f] = text
    try:
        asts[f] = ast.parse(text)
    except SyntaxError as e:
        syntax_errors[rel(f)] = str(e)

imports_by_file = defaultdict(list)
imported_modules = set()
functions_by_file = defaultdict(list)
classes_by_file = defaultdict(list)
routes = []
calls = Counter()
defs = Counter()
file_hashes = defaultdict(list)
function_hashes = defaultdict(list)

for f, tree in asts.items():
    text = all_text[f]
    file_hashes[sha256_text(text)].append(rel(f))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports_by_file[rel(f)].append(a.name)
                imported_modules.add(a.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            imports_by_file[rel(f)].append(mod)
            imported_modules.add(mod.split(".")[-1])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs[node.name] += 1
            functions_by_file[rel(f)].append({
                "name": node.name,
                "lineno": node.lineno,
                "args": [a.arg for a in node.args.args],
            })
            try:
                src = ast.get_source_segment(text, node) or node.name
                function_hashes[sha256_text(src)].append(f"{rel(f)}::{node.name}:{node.lineno}")
            except Exception:
                pass
        elif isinstance(node, ast.ClassDef):
            classes_by_file[rel(f)].append({
                "name": node.name,
                "lineno": node.lineno,
            })
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls[node.func.id] += 1
            elif isinstance(node.func, ast.Attribute):
                calls[node.func.attr] += 1

            # FastAPI route decorators
        if hasattr(node, "decorator_list"):
            for dec in getattr(node, "decorator_list", []):
                raw = ast.unparse(dec) if hasattr(ast, "unparse") else ""
                if any(x in raw for x in [".get(", ".post(", ".put(", ".delete(", ".patch(", "api_route"]):
                    routes.append({
                        "file": rel(f),
                        "line": getattr(node, "lineno", None),
                        "function": getattr(node, "name", None),
                        "decorator": raw,
                    })

route_hits = set(x["file"] for x in routes)

test_text = "\n".join(all_text[f] for f in PY_FILES if "/tests/" in ("/" + rel(f)))
test_hits = set()
for f in PY_FILES:
    if f.stem in test_text or module_name_from_path(f) in test_text:
        test_hits.add(rel(f))

master = []
execution = []
orphan = []
deadcode = []
experimental = []
integration = []

for f in PY_FILES:
    text = all_text[f]
    r = rel(f)
    status, tags = classify_file(f, text, imports_by_file, imported_modules, route_hits, test_hits)

    importable = False
    import_error = None
    modname = module_name_from_path(f)

    if r.startswith("app/") or r.startswith("services/"):
        try:
            spec = importlib.util.spec_from_file_location(f"_level_c_probe_{abs(hash(r))}", str(f))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                importable = True
        except Exception as e:
            import_error = repr(e)

    funcs = functions_by_file.get(r, [])
    classes = classes_by_file.get(r, [])

    record = {
        "file": r,
        "module": modname,
        "status": "BROKEN" if r in syntax_errors else status,
        "tags": tags,
        "importable_probe": importable,
        "import_error": import_error,
        "functions": funcs,
        "classes": classes,
        "is_route_file": r in route_hits,
        "is_test_referenced": r in test_hits,
        "imported_by_name_detected": f.stem in imported_modules,
        "line_count": len(text.splitlines()),
    }
    master.append(record)

    if record["status"] in ["ORPHAN", "UNUSED"]:
        orphan.append(record)

    for fn in funcs:
        name = fn["name"]
        if name.startswith("_"):
            continue
        if calls[name] == 0 and not name.startswith("test_"):
            deadcode.append({
                "file": r,
                "function": name,
                "line": fn["lineno"],
                "reason": "defined_but_no_ast_call_detected",
            })

    low = text.lower()
    if any(w in low or w in f.stem.lower() for w in KEYWORDS["experimental"]):
        action = "keep"
        if record["status"] in ["ACTIVE"]:
            action = "promote_candidate"
        elif record["status"] in ["ORPHAN", "UNUSED"]:
            action = "archive_candidate"
        experimental.append({
            "file": r,
            "status": record["status"],
            "recommended_action": action,
            "tags": tags,
        })

    value_score = 0
    value_reasons = []
    for word in ["memory", "planner", "simulation", "orchestrator", "pipeline", "whatsapp", "eldora", "trader", "agent", "graph", "diagnostic"]:
        if word in low or word in f.stem.lower():
            value_score += 1
            value_reasons.append(word)

    if record["status"] in ["ORPHAN", "UNUSED", "PARTIAL", "SHADOW"] and value_score > 0:
        integration.append({
            "file": r,
            "status": record["status"],
            "value_score": value_score,
            "value_reasons": value_reasons,
            "recommendation": "audit_for_possible_integration" if value_score >= 2 else "review_low_priority",
        })

dup_files = [
    {"hash": h, "files": files}
    for h, files in file_hashes.items()
    if len(files) > 1
]

dup_functions = [
    {"hash": h, "locations": locs}
    for h, locs in function_hashes.items()
    if len(locs) > 1
]

dup_names = [
    {"function": name, "definition_count": count}
    for name, count in defs.items()
    if count > 1 and not name.startswith("test_")
]

duplication = {
    "duplicate_files": dup_files,
    "duplicate_functions_exact": dup_functions,
    "duplicate_function_names": dup_names,
    "routes": routes,
}

summary = {
    "generated_at": datetime.now().isoformat(),
    "root": str(ROOT),
    "total_python_files": len(PY_FILES),
    "total_routes_detected": len(routes),
    "status_counts": dict(Counter(x["status"] for x in master)),
    "syntax_errors": syntax_errors,
    "orphan_count": len(orphan),
    "deadcode_candidates": len(deadcode),
    "experimental_count": len(experimental),
    "integration_candidates": len(integration),
    "duplicate_file_groups": len(dup_files),
    "duplicate_function_groups": len(dup_functions),
    "duplicate_function_name_groups": len(dup_names),
}

def write_json(name, data):
    path = REPORT_DIR / name
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

write_json("LEVEL_C_MASTER_MATRIX.json", {"summary": summary, "items": master})
write_json("LEVEL_C_EXECUTION_AUDIT.json", {"summary": summary, "items": execution, "master_importability_included": True})
write_json("LEVEL_C_DUPLICATION_REPORT.json", duplication)
write_json("LEVEL_C_ORPHAN_REPORT.json", {"summary": summary, "items": orphan})
write_json("LEVEL_C_DEADCODE_REPORT.json", {"summary": summary, "items": deadcode})
write_json("LEVEL_C_EXPERIMENTAL_REPORT.json", {"summary": summary, "items": experimental})
write_json("LEVEL_C_INTEGRATION_OPPORTUNITIES.json", {
    "summary": summary,
    "ranking": sorted(integration, key=lambda x: x["value_score"], reverse=True)
})

md = []
md.append("# DOSSIER LEVEL C FULL AUDIT\n")
md.append(f"Generated: {summary['generated_at']}\n")
md.append("## Summary\n")
for k, v in summary.items():
    md.append(f"- **{k}**: `{v}`")
md.append("\n## Status Counts\n")
for k, v in summary["status_counts"].items():
    md.append(f"- {k}: {v}")
md.append("\n## Highest Priority Integration Candidates\n")
for item in sorted(integration, key=lambda x: x["value_score"], reverse=True)[:50]:
    md.append(f"- `{item['file']}` — {item['status']} — score={item['value_score']} — {', '.join(item['value_reasons'])}")
md.append("\n## Orphan / Unused Candidates\n")
for item in orphan[:100]:
    md.append(f"- `{item['file']}` — {item['status']} — tags={item['tags']}")
md.append("\n## Dead Code Candidates\n")
for item in deadcode[:100]:
    md.append(f"- `{item['file']}::{item['function']}` line {item['line']} — {item['reason']}")
md.append("\n## Recommendations\n")
md.append("1. Não remover nada automaticamente nesta fase.")
md.append("2. Promover primeiro capacidades com score alto ligadas a memory, planner, simulation, pipeline, whatsapp, eldora e trader.")
md.append("3. Arquivar apenas após teste seletivo e confirmação de ausência de consumo.")
md.append("4. Criar testes antes de qualquer promoção de capability.")
md.append("5. Manter produção bloqueada até nova certificação.")
(REPORT_DIR / "DOSSIER_LEVEL_C_FULL_AUDIT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, indent=2, ensure_ascii=False))
