from pathlib import Path
import os, json, subprocess, re
from datetime import datetime, timezone

ROOT = Path.cwd()
EVID = Path(os.environ["P19P38M_EVID"])
EVID.mkdir(parents=True, exist_ok=True)

CRITICAL = {
    "app/api/whatsapp.py",
    "app/runtime/cognitive_pipeline.py",
    "app/api/eldora_core_runtime.py",
}

RUNTIME_PREFIXES = (
    "app/runtime/",
    "app/api/",
    "app/eldora/core/",
    "app/retrieval/",
    "app/embedding/",
    "app/humanization/",
)

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return p.stdout

status = run("git status --short").splitlines()

targets = []
for line in status:
    if not line.startswith(" M "):
        continue
    path = line[3:].strip().replace("\\", "/")
    if path in CRITICAL or any(path.startswith(p) for p in RUNTIME_PREFIXES):
        targets.append(path)

targets = sorted(set(targets))

def diff(path):
    return run(f'git diff -- "{path}"')

def classify(path, d):
    added = sum(1 for x in d.splitlines() if x.startswith("+") and not x.startswith("+++"))
    removed = sum(1 for x in d.splitlines() if x.startswith("-") and not x.startswith("---"))
    hunks = sum(1 for x in d.splitlines() if x.startswith("@@"))
    low = d.lower()

    risk = "LOW"
    decision = "KEEP_CANDIDATE_AFTER_TESTS"
    reason = "small or telemetry-like tracked diff"

    if path in CRITICAL:
        risk = "CRITICAL"
        decision = "BLOCK_P19P39_UNTIL_RESOLVED"
        reason = "critical runtime file modified"

    elif any(x in low for x in ["return ", "raise ", "webhook", "twilio", "pipeline", "route", "guard"]):
        risk = "HIGH"
        decision = "MANUAL_REVIEW_BEFORE_COMMIT"
        reason = "runtime behavior keywords present"

    elif removed > 0:
        risk = "HIGH"
        decision = "MANUAL_REVIEW_BEFORE_COMMIT"
        reason = "tracked file has removed lines"

    elif added > 50:
        risk = "MEDIUM"
        decision = "ISOLATE_SEPARATE_COMMIT_AFTER_TESTS"
        reason = "large additive runtime diff"

    return {
        "added_lines": added,
        "removed_lines": removed,
        "hunks": hunks,
        "risk": risk,
        "decision": decision,
        "reason": reason,
    }

reviews = []

for path in targets:
    d = diff(path)
    safe = path.replace("/", "__").replace(":", "_")
    (EVID / f"DIFF_{safe}.diff").write_text(d, encoding="utf-8")
    reviews.append({
        "path": path,
        **classify(path, d),
    })

counts = {}
for r in reviews:
    counts[r["decision"]] = counts.get(r["decision"], 0) + 1

blockers = [r for r in reviews if r["decision"] in {
    "BLOCK_P19P39_UNTIL_RESOLVED",
    "MANUAL_REVIEW_BEFORE_COMMIT",
}]

summary = {
    "mission": "P19P38_M_TRACKED_RUNTIME_FORENSIC_AUDIT",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "tracked_runtime_modified": len(reviews),
    "blocking_files": len(blockers),
    "p19p39_allowed": len(blockers) == 0,
    "decision_counts": counts,
}

(EVID / "tracked_runtime_reviews.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")
(EVID / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# P19P38-M Tracked Runtime Forensic Audit")
md.append("")
for k,v in summary.items():
    md.append(f"- {k}: {v}")
md.append("")
md.append("## Reviews")
for r in reviews:
    md.append(f"- {r['path']} | +{r['added_lines']} -{r['removed_lines']} | hunks={r['hunks']} | risk={r['risk']} | decision={r['decision']} | {r['reason']}")
md.append("")
md.append("## Blocking Files")
for r in blockers:
    md.append(f"- {r['path']} | {r['decision']} | {r['reason']}")
md.append("")
md.append("## Safety")
md.append("- No files restored")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("")
md.append("## Next")
if blockers:
    md.append("P19P38-N TRACKED RUNTIME CLEAN SPLIT PLAN")
else:
    md.append("P19P39 ADAPTER-ONLY SHADOW WIRING")

(EVID / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
