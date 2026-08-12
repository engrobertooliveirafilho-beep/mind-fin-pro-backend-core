from pathlib import Path
import json
import os
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38C_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

def run_lines(cmd: str):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return p.stdout.splitlines()

status = run_lines("git status --short")
untracked = run_lines("git ls-files --others --exclude-standard")
tracked = run_lines("git ls-files")

candidate_paths = []

for line in status:
    if not line.strip():
        continue
    path = line[3:].strip()
    if path.startswith("app/") or path.startswith("tests/"):
        candidate_paths.append(path)

for path in untracked:
    if (path.startswith("app/") or path.startswith("tests/")) and path not in candidate_paths:
        candidate_paths.append(path)

candidate_paths = sorted(set(candidate_paths))

all_code_files = []
for base in ["app", "tests"]:
    root = ROOT / base
    if root.exists():
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in [".py", ".json"]:
                rel = p.relative_to(ROOT).as_posix()
                all_code_files.append(rel)

def read_text(path):
    try:
        return (ROOT / path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

corpus = {}
for p in all_code_files:
    corpus[p] = read_text(p)

def module_name_from_path(path):
    p = path.replace("/", ".")
    if p.endswith(".py"):
        p = p[:-3]
    if p.endswith(".__init__"):
        p = p[:-9]
    return p

def basename_token(path):
    return Path(path).stem

core_markers = [
    "safe_recovery_adapter",
    "relationship_memory_store",
    "long_term_goal_tracker",
    "digital_twin_real",
    "behavior_modeling",
    "emotional_continuity_real",
    "long_term_memory_real",
    "self_reflection_engine",
    "live_cognition_gated",
    "whatsapp",
    "main",
    "cognitive_pipeline",
    "generic_topic_memory_engine",
    "memory_adapter",
    "memory_store",
]

danger_markers = [
    "whatsapp",
    "main.py",
    "cognitive_pipeline",
    "semantic_provider",
    "provider.py",
    "distributed_runtime",
    "event_bus",
    "audit_ledger",
    "forensic",
    "final_output_guard",
]

rows = []

for path in candidate_paths:
    full = ROOT / path
    exists = full.exists()
    text = read_text(path) if exists else ""
    mod = module_name_from_path(path)
    token = basename_token(path)

    references = []
    for other, content in corpus.items():
        if other == path:
            continue
        if mod in content or token in content:
            references.append(other)

    test_refs = [r for r in references if r.startswith("tests/")]
    app_refs = [r for r in references if r.startswith("app/")]

    classification = "ORPHAN_CANDIDATE"
    reason = "no references found"

    lower = path.lower()

    if any(m in lower for m in danger_markers):
        classification = "DANGEROUS_TO_TOUCH"
        reason = "runtime/router/provider/forensic marker"
    elif any(m in lower for m in core_markers):
        classification = "ACTIVE_CORE"
        reason = "matches cognition/runtime core marker"
    elif app_refs:
        classification = "CONNECTED_SUPPORT"
        reason = f"referenced by app code: {len(app_refs)}"
    elif test_refs:
        classification = "LEGACY_REVIEW"
        reason = f"referenced by tests only: {len(test_refs)}"
    elif path.startswith("tests/"):
        classification = "LEGACY_REVIEW"
        reason = "test file without app reference"
    elif path.endswith("__init__.py"):
        classification = "CONNECTED_SUPPORT"
        reason = "package initializer"
    elif path.endswith(".json"):
        classification = "MANUAL_REVIEW"
        reason = "json config/manifest requires manual review"

    rows.append({
        "path": path,
        "exists": exists,
        "module": mod,
        "token": token,
        "references_total": len(references),
        "app_references": app_refs[:25],
        "test_references": test_refs[:25],
        "classification": classification,
        "reason": reason,
    })

counts = {}
for r in rows:
    counts[r["classification"]] = counts.get(r["classification"], 0) + 1

summary = {
    "mission": "P19P38_C_ORPHAN_MODULE_CLASSIFICATION",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "candidate_count": len(rows),
    "counts": counts,
}

(OUT / "orphan_classification.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

csv_lines = ["classification,path,exists,references_total,reason"]
for r in rows:
    csv_lines.append(
        f'{r["classification"]},"{r["path"]}",{r["exists"]},{r["references_total"]},"{r["reason"]}"'
    )
(OUT / "orphan_classification.csv").write_text("\n".join(csv_lines), encoding="utf-8")

md = []
md.append("# P19P38-C Orphan Module Classification")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append(f"Candidate count: {summary['candidate_count']}")
md.append("")
md.append("## Counts")
for k, v in sorted(counts.items()):
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Critical: Dangerous To Touch")
for r in [x for x in rows if x["classification"] == "DANGEROUS_TO_TOUCH"][:80]:
    md.append(f"- {r['path']} | refs={r['references_total']} | {r['reason']}")
md.append("")
md.append("## Active Core")
for r in [x for x in rows if x["classification"] == "ACTIVE_CORE"][:80]:
    md.append(f"- {r['path']} | refs={r['references_total']} | {r['reason']}")
md.append("")
md.append("## Orphan Candidates")
for r in [x for x in rows if x["classification"] == "ORPHAN_CANDIDATE"][:120]:
    md.append(f"- {r['path']} | refs={r['references_total']} | {r['reason']}")
md.append("")
md.append("## Safety")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("- Classification only")
md.append("")
md.append("## Next")
md.append("P19P38-D COGNITION INTEGRATION MAP")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
