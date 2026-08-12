from pathlib import Path
import json
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(r"_evidence\P19P38_REPOSITORY_SANITIZATION_AND_COGNITION_BASELINE_20260622_141617")
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }

git_status = run("git status --short")
untracked = run("git ls-files --others --exclude-standard")

deleted = [
    line[3:] for line in git_status["stdout"].splitlines()
    if line.startswith(" D ") or line.startswith("D ")
]

modified = [
    line[3:] for line in git_status["stdout"].splitlines()
    if line.startswith(" M ") or line.startswith("M ")
]

unknown = untracked["stdout"].splitlines()

def classify(path: str):
    p = path.replace("\\\\", "/")
    name = Path(p).name.lower()

    if p.startswith("_evidence/") or p.startswith("evidence/"):
        return "EVIDENCE"
    if ".bak" in name or name.endswith(".bak") or "rollback" in name:
        return "BACKUP_OR_ROLLBACK"
    if name.startswith("_fix") or name.startswith("patch_") or name.startswith("_patch") or name.endswith(".ps1"):
        return "TEMP_SCRIPT_OR_PATCH"
    if p.startswith("tests/"):
        return "TEST"
    if p.startswith("app/"):
        return "APP_CODE"
    if p.startswith("runtime/") or p.startswith("_runtime_state/"):
        return "RUNTIME_STATE"
    if p.startswith("data/") or p.startswith("reports/"):
        return "DATA_OR_REPORT"
    if name.endswith(".json") or name.endswith(".csv") or name.endswith(".txt") or name.endswith(".log"):
        return "ARTIFACT"
    return "OTHER"

inventory = []

for p in unknown:
    inventory.append({
        "path": p,
        "git_state": "UNTRACKED",
        "class": classify(p),
    })

for p in modified:
    inventory.append({
        "path": p,
        "git_state": "MODIFIED",
        "class": classify(p),
    })

for p in deleted:
    inventory.append({
        "path": p,
        "git_state": "DELETED",
        "class": classify(p),
    })

summary = {
    "mission": "P19P38_REPOSITORY_SANITIZATION_AND_COGNITION_BASELINE",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "counts": {
        "inventory_total": len(inventory),
        "untracked": len(unknown),
        "modified": len(modified),
        "deleted": len(deleted),
    },
    "classes": {},
}

for item in inventory:
    summary["classes"][item["class"]] = summary["classes"].get(item["class"], 0) + 1

cleanup_plan = []

for item in inventory:
    cls = item["class"]
    state = item["git_state"]
    path = item["path"]

    if cls in ["BACKUP_OR_ROLLBACK", "TEMP_SCRIPT_OR_PATCH"]:
        action = "MOVE_TO_ARCHIVE_REVIEW"
    elif cls == "EVIDENCE":
        action = "KEEP_OR_EXPORT_TO_DRIVE"
    elif cls == "APP_CODE":
        action = "REVIEW_BEFORE_ANY_CLEANUP"
    elif cls == "TEST":
        action = "REVIEW_AND_CLASSIFY_ACTIVE_OR_LEGACY"
    elif cls == "RUNTIME_STATE":
        action = "DO_NOT_COMMIT_RUNTIME_STATE"
    elif state == "DELETED":
        action = "VERIFY_INTENT_BEFORE_RESTORE_OR_COMMIT_DELETE"
    else:
        action = "MANUAL_REVIEW"

    cleanup_plan.append({
        "path": path,
        "git_state": state,
        "class": cls,
        "recommended_action": action,
    })

cognition_files = [
    "app/companionship/safe_recovery_adapter.py",
    "app/companionship/relationship_memory_store.py",
    "app/companionship/long_term_goal_tracker.py",
    "app/companionship/digital_twin_real.py",
    "app/companionship/behavior_modeling.py",
    "app/companionship/emotional_continuity_real.py",
    "app/companionship/long_term_memory_real.py",
    "app/companionship/self_reflection_engine.py",
    "app/companionship/live_cognition_gated.py",
]

cognition_baseline = []

for f in cognition_files:
    p = ROOT / f
    cognition_baseline.append({
        "path": f,
        "exists": p.exists(),
        "size": p.stat().st_size if p.exists() else 0,
        "class": "COGNITION_CORE",
    })

(OUT / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "cleanup_plan.json").write_text(json.dumps(cleanup_plan, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "cognition_baseline.json").write_text(json.dumps(cognition_baseline, ensure_ascii=False, indent=2), encoding="utf-8")

critical = [
    x for x in inventory
    if x["class"] in ["APP_CODE", "TEST", "RUNTIME_STATE"]
]

md = []
md.append("# P19P38 Repository Sanitization and Cognition Baseline")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Counts")
for k, v in summary["counts"].items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Classes")
for k, v in sorted(summary["classes"].items()):
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Critical Review Required")
for item in critical[:120]:
    md.append(f"- {item['git_state']} | {item['class']} | {item['path']}")
md.append("")
md.append("## Cognition Baseline")
for item in cognition_baseline:
    md.append(f"- {item['path']} | exists={item['exists']} | size={item['size']}")
md.append("")
md.append("## Rule")
md.append("No files were deleted or moved. This mission is audit-only.")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
