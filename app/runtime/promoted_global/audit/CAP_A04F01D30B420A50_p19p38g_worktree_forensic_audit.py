from pathlib import Path
import json
import os
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38G_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return p.stdout.splitlines()

status = run("git status --short")
untracked = run("git ls-files --others --exclude-standard")
tracked = run("git ls-files")

items = []

def classify_path(path: str):
    p = path.replace("\\", "/")
    n = Path(p).name.lower()

    if p.startswith("app/api/whatsapp.py") or p.startswith("app/runtime/cognitive_pipeline.py"):
        return "CRITICAL_RUNTIME"
    if p.startswith("app/companionship/"):
        return "COGNITION_CORE"
    if p.startswith("app/"):
        return "APP_CODE"
    if p.startswith("tests/"):
        return "TEST"
    if p.startswith("_evidence/"):
        return "EVIDENCE"
    if p.startswith("runtime/") or p.startswith("_runtime_state/"):
        return "RUNTIME_STATE"
    if n.endswith(".ps1") or n.startswith("_fix") or n.startswith("patch_"):
        return "SCRIPT_PATCH"
    if ".bak" in n or "rollback" in n:
        return "BACKUP"
    if p.startswith("data/") or p.startswith("reports/") or n.endswith(".json") or n.endswith(".txt"):
        return "ARTIFACT"
    return "OTHER"

for line in status:
    if not line.strip():
        continue
    state = line[:2].strip()
    path = line[3:].strip()
    items.append({
        "state": state,
        "path": path,
        "class": classify_path(path),
    })

for path in untracked:
    if not any(x["path"] == path for x in items):
        items.append({
            "state": "??",
            "path": path,
            "class": classify_path(path),
        })

risk = {
    "CRITICAL_BLOCKER": [],
    "HIGH_REVIEW": [],
    "MEDIUM_REVIEW": [],
    "LOW_NOISE": [],
}

for item in items:
    cls = item["class"]
    state = item["state"]

    if cls == "CRITICAL_RUNTIME" and state in ["M", "D", "??"]:
        risk["CRITICAL_BLOCKER"].append(item)
    elif cls in ["COGNITION_CORE", "APP_CODE"] and state in ["M", "D", "??"]:
        risk["HIGH_REVIEW"].append(item)
    elif cls in ["TEST", "RUNTIME_STATE"] and state in ["M", "D", "??"]:
        risk["MEDIUM_REVIEW"].append(item)
    else:
        risk["LOW_NOISE"].append(item)

summary = {
    "mission": "P19P38_G_WORKTREE_FORENSIC_AUDIT",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "items_total": len(items),
    "critical_blockers": len(risk["CRITICAL_BLOCKER"]),
    "high_review": len(risk["HIGH_REVIEW"]),
    "medium_review": len(risk["MEDIUM_REVIEW"]),
    "low_noise": len(risk["LOW_NOISE"]),
    "p19p39_allowed": len(risk["CRITICAL_BLOCKER"]) == 0,
}

recommendation = []

if risk["CRITICAL_BLOCKER"]:
    recommendation.append("BLOCK P19P39 until critical runtime modifications are reviewed.")
    recommendation.append("Do not patch safe_recovery_adapter while app/api/whatsapp.py or app/runtime/cognitive_pipeline.py are dirty.")
else:
    recommendation.append("P19P39 may proceed with adapter-only shadow wiring.")
    recommendation.append("Do not patch app/api/whatsapp.py.")
    recommendation.append("Do not patch app/runtime/cognitive_pipeline.py.")

recommendation.append("Commit only explicit files.")
recommendation.append("Do not run git add .")
recommendation.append("Do not clean untracked files automatically.")

(OUT / "worktree_forensic_items.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "risk_groups.json").write_text(json.dumps(risk, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "recommendation.json").write_text(json.dumps(recommendation, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# P19P38-G Worktree Forensic Audit")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## Critical Blockers")
for x in risk["CRITICAL_BLOCKER"][:80]:
    md.append(f"- {x['state']} | {x['class']} | {x['path']}")
md.append("")
md.append("## High Review")
for x in risk["HIGH_REVIEW"][:120]:
    md.append(f"- {x['state']} | {x['class']} | {x['path']}")
md.append("")
md.append("## Recommendation")
for r in recommendation:
    md.append(f"- {r}")
md.append("")
md.append("## Rule")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("- Audit only")
md.append("")
md.append("## Next")
md.append("If p19p39_allowed=True: P19P39 ADAPTER-ONLY SHADOW WIRING")
md.append("If p19p39_allowed=False: P19P38-H CRITICAL RUNTIME DIFF REVIEW")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
