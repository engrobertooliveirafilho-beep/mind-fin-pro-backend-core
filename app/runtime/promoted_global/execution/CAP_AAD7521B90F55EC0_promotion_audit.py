from pathlib import Path
import json, os, ast
from datetime import datetime, timezone

ROOT = Path.cwd()
EVID = Path(os.environ.get("EVID","."))

WHITELIST = [
"app/companionship/self_reflection_engine.py",
"app/runtime/capability_orchestrator.py",
"app/runtime/capability_recovery_bridge.py",
"app/runtime/capability_usage_ledger.py",
"app/runtime/drive_capability_absorption.py",
"app/runtime/followup_unified_resolver.py",
"app/runtime/knowledge_extraction_engine.py",
"app/runtime/memory_adapter.py",
"app/runtime/memory_store.py",
"app/runtime/p19_unified_pipeline.py",
"app/p7_adapters",
"app/p8_shadow",
"app/p9_runtime_consumption",
"app/p10_activation_stack",
"app/p16_real_use_case",
"app/p17_value_proof",
"app/p18_conversational_execution",
"app/p19_real_world_validation",
]

def py_files(p):
    path = ROOT / p
    if path.is_file() and path.suffix == ".py":
        return [path]
    if path.is_dir():
        return list(path.rglob("*.py"))
    return []

rows=[]
for item in WHITELIST:
    files=py_files(item)
    total_funcs=0
    syntax_ok=True
    errors=[]
    flags=0
    tests=0
    for f in files:
        txt=f.read_text(encoding="utf-8", errors="ignore")
        try:
            tree=ast.parse(txt)
            total_funcs += sum(isinstance(n,(ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for n in ast.walk(tree))
        except Exception as e:
            syntax_ok=False
            errors.append(f"{f.relative_to(ROOT)}: {e}")
        if "os.getenv" in txt or "ENABLED" in txt or "SHADOW" in txt:
            flags+=1
    key=Path(item).name.replace(".py","")
    for t in (ROOT/"tests").rglob("test*.py") if (ROOT/"tests").exists() else []:
        if key in t.read_text(encoding="utf-8", errors="ignore"):
            tests+=1

    if not files:
        status="MISSING"
    elif not syntax_ok:
        status="BLOCKED_SYNTAX"
    elif tests > 0 and flags > 0:
        status="PRODUCTION_CANDIDATE"
    elif tests > 0 or flags > 0:
        status="SHADOW_CANDIDATE"
    else:
        status="ARCHIVE_ONLY"

    rows.append({
        "path": item,
        "files": len(files),
        "symbols": total_funcs,
        "syntax_ok": syntax_ok,
        "flags_or_shadow_hits": flags,
        "test_refs": tests,
        "status": status,
        "errors": errors[:10]
    })

counts={}
for r in rows:
    counts[r["status"]] = counts.get(r["status"],0)+1

summary={
    "mission":"P19P38_Q_CAPABILITY_PROMOTION_AUDIT",
    "status":"AUDIT_ONLY_PASS",
    "runtime_modified":False,
    "files_moved":False,
    "files_deleted":False,
    "generated_at":datetime.now(timezone.utc).isoformat(),
    "items":len(rows),
    "counts":counts
}

(EVID/"promotion_audit.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
(EVID/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")

md=["# P19P38-Q Capability Promotion Audit",""]
for k,v in summary.items(): md.append(f"- {k}: {v}")
md += ["","## Decisions"]
for r in rows:
    md.append(f"- {r['path']} | {r['status']} | files={r['files']} | symbols={r['symbols']} | tests={r['test_refs']} | flags={r['flags_or_shadow_hits']}")
md += ["","## Next","P19P39 adapter-only shadow wiring for PRODUCTION_CANDIDATE + selected SHADOW_CANDIDATE only."]
(EVID/"REPORT.md").write_text("\n".join(md),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))
