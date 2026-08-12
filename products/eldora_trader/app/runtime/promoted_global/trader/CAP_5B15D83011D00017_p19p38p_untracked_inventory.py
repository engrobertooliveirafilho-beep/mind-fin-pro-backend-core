from pathlib import Path
import os, json, subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
EVID = Path(os.environ["P19P38P_EVID"])
EVID.mkdir(parents=True, exist_ok=True)

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return p.stdout.splitlines()

untracked = run("git ls-files --others --exclude-standard")

def classify(path):
    p = path.replace("\\", "/")

    if p.startswith("_quarantine/") or p.startswith("_runtime_split_backup/") or p.startswith("_worktree_backup/"):
        return "BACKUP_OR_QUARANTINE"

    if p.startswith("app/companionship/"):
        return "ELDORA_COMPANION_COGNITION"

    if p.startswith("app/runtime/p20") or p.startswith("app/runtime/p21") or p.startswith("app/runtime/p22") or "ftmo" in p.lower() or "paper" in p.lower():
        return "TRADER_FTMO_RUNTIME"

    if p.startswith("app/runtime/"):
        return "ELDORA_RUNTIME_SUPPORT"

    if p.startswith("app/p7_") or p.startswith("app/p8_") or p.startswith("app/p9_") or p.startswith("app/p10_") or p.startswith("app/p12_") or p.startswith("app/p16_") or p.startswith("app/p17") or p.startswith("app/p18") or p.startswith("app/p19"):
        return "ELDORA_PROGRAM_LAYER"

    if p.startswith("app/mind/") or "p55" in p.lower() or "p56" in p.lower() or "pedigree" in p.lower() or "bovine" in p.lower():
        return "P55_P56_BOVINE_STACK"

    if p.startswith("tests/"):
        return "TESTS_UNTRACKED"

    if p.startswith("data/") or p.startswith("reports/") or p.startswith("runtime/") or p.endswith(".json"):
        return "DATA_RUNTIME_ARTIFACT"

    if p.startswith("supabase/"):
        return "SUPABASE_ARTIFACT"

    if p.endswith(".bak") or ".bak" in p:
        return "BACKUP_FILE"

    return "MANUAL_REVIEW"

items = []

for path in untracked:
    full = ROOT / path
    size = full.stat().st_size if full.exists() and full.is_file() else 0
    items.append({
        "path": path,
        "class": classify(path),
        "is_dir": full.is_dir(),
        "size": size,
    })

counts = {}
for i in items:
    counts[i["class"]] = counts.get(i["class"], 0) + 1

summary = {
    "mission": "P19P38_P_UNTRACKED_MODULE_INVENTORY",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "untracked_total": len(items),
    "counts": counts,
}

(EVID / "untracked_inventory.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
(EVID / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

csv = ["class,path,is_dir,size"]
for i in items:
    csv.append(f'{i["class"]},"{i["path"]}",{i["is_dir"]},{i["size"]}')
(EVID / "untracked_inventory.csv").write_text("\n".join(csv), encoding="utf-8")

md = []
md.append("# P19P38-P Untracked Module Inventory")
md.append("")
for k,v in summary.items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Counts")
for k,v in sorted(counts.items()):
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Priority Buckets")
for bucket in [
    "ELDORA_COMPANION_COGNITION",
    "ELDORA_RUNTIME_SUPPORT",
    "ELDORA_PROGRAM_LAYER",
    "TRADER_FTMO_RUNTIME",
    "P55_P56_BOVINE_STACK",
    "TESTS_UNTRACKED",
    "DATA_RUNTIME_ARTIFACT",
    "BACKUP_OR_QUARANTINE",
    "MANUAL_REVIEW",
]:
    rows = [x for x in items if x["class"] == bucket]
    if rows:
        md.append("")
        md.append(f"### {bucket}")
        for r in rows[:80]:
            md.append(f"- {r['path']}")
md.append("")
md.append("## Safety")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("")
md.append("## Next")
md.append("P19P38-Q stage whitelist for Eldora-only untracked modules")

(EVID / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
