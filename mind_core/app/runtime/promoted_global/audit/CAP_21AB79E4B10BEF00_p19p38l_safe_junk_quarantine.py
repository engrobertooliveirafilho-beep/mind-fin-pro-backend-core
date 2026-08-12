from pathlib import Path
import os, json, shutil, subprocess
from datetime import datetime, timezone

ROOT=Path.cwd()
EVID=Path(os.environ["P19P38L_EVID"])
QUAR=Path(os.environ["P19P38L_QUAR"])
EVID.mkdir(parents=True, exist_ok=True)
QUAR.mkdir(parents=True, exist_ok=True)

def run(cmd):
    p=subprocess.run(cmd,cwd=ROOT,shell=True,capture_output=True,text=True)
    return p.stdout.splitlines()

status=run("git status --short")

SAFE_EXT={".diff",".patch",".log",".tmp",".bak",".old",".ps1",".txt"}
SAFE_NAMES={
    "whatsapp.diff","cognitive.diff","trade_log.txt",
    "youtube_api_debug.py","yt_video_test.py",
    "google_cse_debug.py","google_cse_test.py",
    "custom_search_smoke_test.py","custom_search_siterestrict_test.py",
}
SAFE_PREFIXES=(
    "_fix","patch_","_patch","cleanup_","rollback_",
    "_apply","_force","_rebuild","_semantic","_p412",
)
SAFE_DIRS=(
    "tools/",
    "scripts/",
    "_maintenance/",
    "_institutional/",
)

NEVER_PREFIXES=(
    "app/companionship/",
    "app/runtime/",
    "app/api/whatsapp.py",
    "app/runtime/cognitive_pipeline.py",
    "tests/",
    "app/p",
    "app/eldora/",
    "app/api/eldora_core_runtime.py",
)

def norm(p): return p.replace("\\","/")

def is_untracked(line):
    return line.startswith("?? ")

def classify(path):
    p=norm(path)
    name=Path(p).name
    lower=name.lower()
    suffix=Path(p).suffix.lower()

    if any(p.startswith(x) for x in NEVER_PREFIXES):
        return "KEEP_RUNTIME_OR_CODE"

    if any(p.startswith(x) for x in SAFE_DIRS):
        return "SAFE_QUARANTINE_DIR"

    if name in SAFE_NAMES:
        return "SAFE_QUARANTINE_NAMED"

    if any(lower.startswith(x) for x in SAFE_PREFIXES):
        return "SAFE_QUARANTINE_PATCH_SCRIPT"

    if ".bak" in lower or "backup" in lower or "rollback" in lower:
        return "SAFE_QUARANTINE_BACKUP"

    if suffix in SAFE_EXT:
        return "SAFE_QUARANTINE_EXT"

    return "MANUAL_REVIEW_KEEP"

items=[]
moves=[]

for line in status:
    if not is_untracked(line):
        continue
    path=line[3:].strip()
    cls=classify(path)
    item={"path":path,"class":cls,"moved":False,"dest":None}
    if cls.startswith("SAFE_QUARANTINE"):
        src=ROOT/path
        if src.exists():
            safe=norm(path).replace("/","__").replace(":","_")
            dest=QUAR/safe
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(src),str(dest))
            item["moved"]=True
            item["dest"]=str(dest)
            moves.append(item)
    items.append(item)

rollback=[]
rollback.append("# P19P38-L rollback")
rollback.append("# Moves quarantined files back to original paths.")
rollback.append("")
for m in moves:
    src=m["dest"].replace("\\","/")
    dst=m["path"].replace("\\","/")
    rollback.append(f'New-Item -ItemType Directory -Force (Split-Path "{dst}") | Out-Null')
    rollback.append(f'Move-Item -Force "{src}" "{dst}"')
    rollback.append("")

summary={
    "mission":"P19P38_L_SAFE_JUNK_QUARANTINE",
    "status":"SAFE_QUARANTINE_APPLIED",
    "runtime_modified":False,
    "tracked_files_modified":False,
    "files_deleted":False,
    "generated_at":datetime.now(timezone.utc).isoformat(),
    "untracked_seen":len(items),
    "moved_to_quarantine":len(moves),
    "kept_for_manual_review":sum(1 for x in items if not x["moved"]),
    "quarantine_root":str(QUAR),
}

(EVID/"quarantine_items.json").write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")
(EVID/"moved_manifest.json").write_text(json.dumps(moves,ensure_ascii=False,indent=2),encoding="utf-8")
(EVID/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
(EVID/"ROLLBACK_P19P38L.ps1").write_text("\n".join(rollback),encoding="utf-8")

md=[]
md.append("# P19P38-L Safe Junk Quarantine")
md.append("")
for k,v in summary.items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Safety")
md.append("- Moved only untracked SAFE_QUARANTINE files")
md.append("- Did not touch tracked files")
md.append("- Did not touch app/api/whatsapp.py")
md.append("- Did not touch app/runtime/cognitive_pipeline.py")
md.append("- Rollback script generated")
md.append("")
md.append("## Next")
md.append("Run P19P38-M to re-audit critical blockers and verify P19P39 readiness.")
(EVID/"REPORT.md").write_text("\n".join(md),encoding="utf-8")

print(json.dumps(summary,ensure_ascii=False,indent=2))
