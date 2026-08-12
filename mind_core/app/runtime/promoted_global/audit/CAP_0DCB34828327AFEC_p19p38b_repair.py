from pathlib import Path
import json
import os
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38B_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

def run_lines(cmd: str):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return p.stdout.splitlines()

status = run_lines("git status --short")
untracked = run_lines("git ls-files --others --exclude-standard")

items = []

def classify(path: str):
    p = path.replace("\\", "/")
    n = Path(p).name.lower()

    if p.startswith("_evidence/") or p.startswith("evidence/"):
        return "EVIDENCE"
    if ".bak" in n or "rollback" in n:
        return "BACKUP"
    if n.startswith("_fix") or n.startswith("patch_") or n.startswith("_patch") or n.endswith(".ps1"):
        return "PATCH_OR_SCRIPT"
    if p.startswith("_runtime_state/") or p.startswith("runtime/"):
        return "RUNTIME_STATE"
    if p.startswith("app/"):
        return "APP_CODE"
    if p.startswith("tests/"):
        return "TEST"
    if p.startswith("reports/") or p.startswith("data/"):
        return "DATA_REPORT"
    return "OTHER"

for line in status:
    if not line.strip():
        continue
    state = line[:2].strip()
    path = line[3:].strip()
    items.append({"path": path, "state": state, "class": classify(path)})

for path in untracked:
    if not any(x["path"] == path for x in items):
        items.append({"path": path, "state": "??", "class": classify(path)})

archive_groups = {
    "SAFE_ARCHIVE_CANDIDATES": [],
    "NEVER_AUTO_ARCHIVE": [],
    "MANUAL_REVIEW_REQUIRED": [],
    "RESTORE_REVIEW_REQUIRED": [],
}

for item in items:
    cls = item["class"]
    state = item["state"]

    if state == "D":
        archive_groups["RESTORE_REVIEW_REQUIRED"].append(item)
    elif cls in ["BACKUP", "PATCH_OR_SCRIPT", "EVIDENCE", "DATA_REPORT"]:
        archive_groups["SAFE_ARCHIVE_CANDIDATES"].append(item)
    elif cls in ["APP_CODE", "TEST"]:
        archive_groups["NEVER_AUTO_ARCHIVE"].append(item)
    elif cls == "RUNTIME_STATE":
        archive_groups["MANUAL_REVIEW_REQUIRED"].append(item)
    else:
        archive_groups["MANUAL_REVIEW_REQUIRED"].append(item)

summary = {
    "mission": "P19P38_B_SAFE_ARCHIVE_PLAN_REPAIR",
    "status": "DRY_RUN_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "counts": {k: len(v) for k, v in archive_groups.items()},
}

commands = [
    "# P19P38-B generated dry-run commands",
    "# NOT EXECUTED AUTOMATICALLY",
    "# Review before running.",
    "",
    '$ARCHIVE_ROOT = "_archive/P19P38_REVIEW"',
    'New-Item -ItemType Directory -Force $ARCHIVE_ROOT | Out-Null',
    "",
]

for item in archive_groups["SAFE_ARCHIVE_CANDIDATES"]:
    p = item["path"].replace("/", "\\")
    safe_name = p.replace("\\", "__").replace(":", "_")
    commands.append(f"# MOVE REVIEW: {p}")
    commands.append(f'# Move-Item -Force "{p}" "$(Join-Path $ARCHIVE_ROOT \'{safe_name}\')"')
    commands.append("")

(OUT / "archive_groups.json").write_text(json.dumps(archive_groups, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "DRY_RUN_ARCHIVE_COMMANDS.ps1").write_text("\n".join(commands), encoding="utf-8")

md = []
md.append("# P19P38-B Safe Archive Plan Repair")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Counts")
for k, v in summary["counts"].items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Safety")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("- Commands generated as comments only")
md.append("")
md.append("## Next")
md.append("P19P38-C ORPHAN MODULE CLASSIFICATION")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
