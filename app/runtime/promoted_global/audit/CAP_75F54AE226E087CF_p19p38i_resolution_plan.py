from pathlib import Path
import json
import os
import re
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38I_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/api/whatsapp.py",
    "app/runtime/cognitive_pipeline.py",
]

SAFE_KEYWORDS = [
    "telemetry",
    "shadow",
    "audit",
    "ledger",
    "trace",
    "try:",
    "except Exception",
    "os.getenv",
    "feature",
    "flag",
]

RISKY_KEYWORDS = [
    "return",
    "raise",
    "delete",
    "Body",
    "From",
    "MessageSid",
    "Twilio",
    "Response",
    "TwiML",
    "send",
    "reply",
    "webhook",
    "route",
    "pipeline",
    "final",
    "guard",
]

COGNITION_KEYWORDS = [
    "safe_recovery_adapter",
    "collect_recovered_context",
    "live_cognition",
    "digital_twin",
    "long_term_memory",
    "self_reflection",
    "behavior_model",
    "relationship_memory",
]

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, capture_output=True, text=True)
    return p.stdout

def diff_for(path):
    return run(f'git diff -- "{path}"')

def split_hunks(diff):
    hunks = []
    current = []
    for line in diff.splitlines():
        if line.startswith("@@"):
            if current:
                hunks.append(current)
            current = [line]
        elif current:
            current.append(line)
    if current:
        hunks.append(current)
    return hunks

def classify_hunk(lines):
    text = "\n".join(lines)
    added = [x[1:] for x in lines if x.startswith("+") and not x.startswith("+++")]
    removed = [x[1:] for x in lines if x.startswith("-") and not x.startswith("---")]

    safe_hits = [k for k in SAFE_KEYWORDS if k.lower() in text.lower()]
    risky_hits = [k for k in RISKY_KEYWORDS if k.lower() in text.lower()]
    cognition_hits = [k for k in COGNITION_KEYWORDS if k.lower() in text.lower()]

    if cognition_hits and not removed:
        decision = "POSSIBLY_KEEP_AS_COGNITION_SHADOW"
        risk = "MEDIUM"
    elif risky_hits and removed:
        decision = "REVIEW_MANUALLY_BEFORE_KEEP"
        risk = "HIGH"
    elif risky_hits:
        decision = "REVIEW_MANUALLY_BEFORE_KEEP"
        risk = "HIGH"
    elif safe_hits and not removed:
        decision = "LIKELY_SAFE_TELEMETRY_OR_SHADOW"
        risk = "LOW"
    else:
        decision = "UNKNOWN_REVIEW_REQUIRED"
        risk = "MEDIUM"

    return {
        "header": lines[0] if lines else "",
        "added_lines": len(added),
        "removed_lines": len(removed),
        "safe_hits": safe_hits,
        "risky_hits": risky_hits,
        "cognition_hits": cognition_hits,
        "risk": risk,
        "decision": decision,
        "preview": "\n".join(lines[:40]),
    }

reviews = []

for path in TARGETS:
    diff = diff_for(path)
    hunks = split_hunks(diff)
    hunk_reviews = [classify_hunk(h) for h in hunks]

    high = sum(1 for h in hunk_reviews if h["risk"] == "HIGH")
    medium = sum(1 for h in hunk_reviews if h["risk"] == "MEDIUM")
    low = sum(1 for h in hunk_reviews if h["risk"] == "LOW")

    if high > 0:
        file_decision = "BLOCK_AND_REVIEW_MANUALLY"
        recommended_resolution = "do_not_commit_until_hunks_reviewed"
    elif medium > 0:
        file_decision = "ISOLATE_OR_COMMIT_SEPARATELY_AFTER_REVIEW"
        recommended_resolution = "create dedicated commit after focused tests"
    elif low > 0:
        file_decision = "CAN_COMMIT_AS_TELEMETRY_AFTER_TESTS"
        recommended_resolution = "commit explicitly after tests"
    else:
        file_decision = "NO_DIFF_OR_EMPTY"
        recommended_resolution = "no_action"

    reviews.append({
        "path": path,
        "hunks_total": len(hunk_reviews),
        "risk_counts": {
            "HIGH": high,
            "MEDIUM": medium,
            "LOW": low,
        },
        "file_decision": file_decision,
        "recommended_resolution": recommended_resolution,
        "hunks": hunk_reviews,
    })

blocking = [
    r for r in reviews
    if r["file_decision"] in [
        "BLOCK_AND_REVIEW_MANUALLY",
        "ISOLATE_OR_COMMIT_SEPARATELY_AFTER_REVIEW",
    ]
]

summary = {
    "mission": "P19P38_I_CRITICAL_RUNTIME_RESOLUTION_PLAN",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "targets_total": len(reviews),
    "blocking_files": len(blocking),
    "p19p39_allowed": len(blocking) == 0,
}

if blocking:
    next_action = "P19P38-J critical runtime manual resolution executor"
else:
    next_action = "P19P39 adapter-only shadow wiring"

resolution_plan = []

for r in reviews:
    if r["file_decision"] == "BLOCK_AND_REVIEW_MANUALLY":
        resolution_plan.append({
            "path": r["path"],
            "action": "manual_hunk_review_required",
            "safe_command": f'git diff -- "{r["path"]}"',
            "do_not_run_automatically": True,
        })
    elif r["file_decision"] == "ISOLATE_OR_COMMIT_SEPARATELY_AFTER_REVIEW":
        resolution_plan.append({
            "path": r["path"],
            "action": "isolate_commit_or_restore_after_review",
            "safe_command": f'git diff -- "{r["path"]}"',
            "do_not_run_automatically": True,
        })
    elif r["file_decision"] == "CAN_COMMIT_AS_TELEMETRY_AFTER_TESTS":
        resolution_plan.append({
            "path": r["path"],
            "action": "run_tests_then_commit_explicitly",
            "safe_command": f'git add "{r["path"]}" && git commit -m "reviewed runtime telemetry changes"',
            "do_not_run_automatically": True,
        })
    else:
        resolution_plan.append({
            "path": r["path"],
            "action": "no_action",
            "safe_command": "",
            "do_not_run_automatically": True,
        })

(OUT / "critical_runtime_resolution_plan.json").write_text(json.dumps(resolution_plan, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "critical_runtime_hunk_reviews.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# P19P38-I Critical Runtime Resolution Plan")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## File Decisions")
for r in reviews:
    md.append(f"- {r['path']} | hunks={r['hunks_total']} | risk={r['risk_counts']} | decision={r['file_decision']} | resolution={r['recommended_resolution']}")
md.append("")
md.append("## Resolution Plan")
for r in resolution_plan:
    md.append(f"- {r['path']} | action={r['action']} | auto={not r['do_not_run_automatically']}")
md.append("")
md.append("## Safety")
md.append("- No files restored")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("- Plan only")
md.append("")
md.append("## Next")
md.append(next_action)

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
