from pathlib import Path
import json
import os
import subprocess
import re
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38H_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/api/whatsapp.py",
    "app/runtime/cognitive_pipeline.py",
    "app/api/whatsapp.py.bak_p449c_fix2",
]

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return {
        "returncode": p.returncode,
        "stdout": p.stdout,
        "stderr": p.stderr,
    }

def read(path):
    p = ROOT / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

def diff_for(path):
    if not (ROOT / path).exists():
        return ""
    return run(f'git diff -- "{path}"')["stdout"]

def git_status_for(path):
    lines = run("git status --short")["stdout"].splitlines()
    out = []
    for line in lines:
        if line[3:].strip() == path:
            out.append(line[:2].strip() or "??")
    return out

def count_diff_stats(diff):
    return {
        "added_lines": sum(1 for x in diff.splitlines() if x.startswith("+") and not x.startswith("+++")),
        "removed_lines": sum(1 for x in diff.splitlines() if x.startswith("-") and not x.startswith("---")),
        "hunks": sum(1 for x in diff.splitlines() if x.startswith("@@")),
    }

def extract_risk_tokens(text):
    tokens = []
    patterns = [
        "webhook",
        "Twilio",
        "Body",
        "From",
        "MessageSid",
        "Response",
        "TwiML",
        "cognitive",
        "pipeline",
        "memory",
        "safe_recovery_adapter",
        "collect_recovered_context",
        "os.getenv",
        "feature",
        "live",
        "shadow",
        "return",
        "except Exception",
    ]
    for p in patterns:
        if p.lower() in text.lower():
            tokens.append(p)
    return tokens

def decision_for(path, status, diff_stats, exists):
    if not exists and "D" in status:
        return {
            "decision": "REVIEW_DELETE_BEFORE_ANY_ACTION",
            "reason": "tracked critical file appears deleted",
            "p19p39_blocking": True,
        }

    if path.endswith(".bak_p449c_fix2"):
        return {
            "decision": "ARCHIVE_CANDIDATE_DO_NOT_LOAD_RUNTIME",
            "reason": "backup file should not be imported or used by runtime",
            "p19p39_blocking": False,
        }

    if diff_stats["added_lines"] + diff_stats["removed_lines"] == 0:
        return {
            "decision": "NO_DIFF_ON_TRACKED_FILE",
            "reason": "git diff empty",
            "p19p39_blocking": False,
        }

    return {
        "decision": "CRITICAL_DIFF_REVIEW_REQUIRED",
        "reason": "critical runtime file has uncommitted diff",
        "p19p39_blocking": True,
    }

reviews = []

for path in TARGETS:
    p = ROOT / path
    exists = p.exists()
    text = read(path)
    diff = diff_for(path)
    status = git_status_for(path)
    stats = count_diff_stats(diff)
    decision = decision_for(path, status, stats, exists)

    reviews.append({
        "path": path,
        "exists": exists,
        "git_status": status,
        "size": p.stat().st_size if exists else 0,
        "diff_stats": stats,
        "risk_tokens": extract_risk_tokens(text),
        **decision,
    })

blocking = [r for r in reviews if r["p19p39_blocking"]]

summary = {
    "mission": "P19P38_H_CRITICAL_RUNTIME_DIFF_REVIEW",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "targets_total": len(reviews),
    "blocking_count": len(blocking),
    "p19p39_allowed": len(blocking) == 0,
}

recommendations = []

if blocking:
    recommendations.append("P19P39 remains BLOCKED.")
    recommendations.append("Resolve or explicitly commit/restore critical runtime diffs before adapter wiring.")
    recommendations.append("Do not touch app/api/whatsapp.py or app/runtime/cognitive_pipeline.py in P19P39.")
else:
    recommendations.append("P19P39 may proceed with adapter-only shadow wiring.")
    recommendations.append("Do not modify app/api/whatsapp.py.")
    recommendations.append("Do not modify app/runtime/cognitive_pipeline.py.")

recommendations.append("Backup file may be archived later, but not automatically.")
recommendations.append("Use explicit git add paths only.")

(OUT / "critical_runtime_reviews.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "recommendations.json").write_text(json.dumps(recommendations, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# P19P38-H Critical Runtime Diff Review")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## Reviews")
for r in reviews:
    md.append(f"- {r['path']} | exists={r['exists']} | status={r['git_status']} | decision={r['decision']} | blocking={r['p19p39_blocking']} | diff={r['diff_stats']}")
md.append("")
md.append("## Recommendations")
for r in recommendations:
    md.append(f"- {r}")
md.append("")
md.append("## Safety")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("- Audit only")
md.append("")
md.append("## Next")
md.append("If p19p39_allowed=False: P19P38-I critical runtime resolution plan")
md.append("If p19p39_allowed=True: P19P39 adapter-only shadow wiring")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
