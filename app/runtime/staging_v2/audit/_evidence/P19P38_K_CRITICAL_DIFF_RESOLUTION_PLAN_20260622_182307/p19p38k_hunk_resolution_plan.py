from pathlib import Path
import json
import os
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38K_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/api/whatsapp.py",
    "app/runtime/cognitive_pipeline.py",
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

def classify(text, path):
    lower = text.lower()
    added = [x for x in text.splitlines() if x.startswith("+") and not x.startswith("+++")]
    removed = [x for x in text.splitlines() if x.startswith("-") and not x.startswith("---")]

    has_runtime = any(x in lower for x in [
        "webhook", "twilio", "body", "from", "messagesid", "response", "twiml",
        "return", "route", "pipeline", "guard", "reply"
    ])

    has_cognition = any(x in lower for x in [
        "safe_recovery_adapter", "collect_recovered_context", "memory",
        "digital_twin", "self_reflection", "live_cognition", "shadow"
    ])

    has_telemetry = any(x in lower for x in [
        "telemetry", "trace", "ledger", "audit", "forensic"
    ])

    if removed:
        return {
            "decision": "REVERT_OR_MANUAL_KEEP",
            "risk": "HIGH",
            "reason": "hunk removes existing runtime behavior",
        }

    if path.endswith("whatsapp.py") and has_runtime:
        return {
            "decision": "MANUAL_KEEP_ONLY_AFTER_WEBHOOK_TEST",
            "risk": "HIGH",
            "reason": "WhatsApp runtime path modified",
        }

    if path.endswith("cognitive_pipeline.py") and has_runtime and has_cognition:
        return {
            "decision": "ISOLATE_IN_SEPARATE_COMMIT_AFTER_TESTS",
            "risk": "MEDIUM",
            "reason": "cognition additive inside pipeline",
        }

    if has_cognition and not has_runtime:
        return {
            "decision": "MOVE_TO_ADAPTER_OR_SEPARATE_COMMIT",
            "risk": "MEDIUM",
            "reason": "cognition code should not be mixed into critical runtime",
        }

    if has_telemetry:
        return {
            "decision": "KEEP_TELEMETRY_CANDIDATE",
            "risk": "LOW",
            "reason": "telemetry-only additive candidate",
        }

    return {
        "decision": "UNKNOWN_REVIEW_REQUIRED",
        "risk": "HIGH",
        "reason": "insufficient confidence",
    }

reviews = []
commands = [
    "# P19P38-K DRY-RUN ONLY",
    "# Commands are intentionally commented.",
    "# Review each hunk before applying anything.",
    "",
]

for path in TARGETS:
    diff = diff_for(path)
    hunks = split_hunks(diff)

    for idx, hunk in enumerate(hunks, start=1):
        text = "\n".join(hunk)
        result = classify(text, path)
        hunk_name = f"HUNK_{path.replace('/', '__')}_{idx}.diff"
        (OUT / hunk_name).write_text(text, encoding="utf-8")

        added = [x for x in hunk if x.startswith("+") and not x.startswith("+++")]
        removed = [x for x in hunk if x.startswith("-") and not x.startswith("---")]

        item = {
            "path": path,
            "hunk_index": idx,
            "hunk_file": hunk_name,
            "added_lines": len(added),
            "removed_lines": len(removed),
            **result,
        }
        reviews.append(item)

        commands.append(f"# {path} H{idx} => {result['decision']} | risk={result['risk']}")
        commands.append(f"# Review file: {OUT.as_posix()}/{hunk_name}")
        commands.append(f'# git diff -- "{path}"')
        commands.append("")

counts = {}
for r in reviews:
    counts[r["decision"]] = counts.get(r["decision"], 0) + 1

blocking = [
    r for r in reviews
    if r["decision"] in [
        "REVERT_OR_MANUAL_KEEP",
        "MANUAL_KEEP_ONLY_AFTER_WEBHOOK_TEST",
        "UNKNOWN_REVIEW_REQUIRED",
        "MOVE_TO_ADAPTER_OR_SEPARATE_COMMIT",
        "ISOLATE_IN_SEPARATE_COMMIT_AFTER_TESTS",
    ]
]

summary = {
    "mission": "P19P38_K_CRITICAL_DIFF_RESOLUTION_PLAN",
    "status": "DRY_RUN_PLAN_ONLY",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "hunks_total": len(reviews),
    "blocking_hunks": len(blocking),
    "p19p39_allowed": len(blocking) == 0,
    "decision_counts": counts,
}

(OUT / "hunk_resolution_plan.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "DRY_RUN_COMMANDS.ps1").write_text("\n".join(commands), encoding="utf-8")

md = []
md.append("# P19P38-K Critical Diff Resolution Plan")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## Hunk Resolution")
for r in reviews:
    md.append(
        f"- {r['path']} H{r['hunk_index']} | +{r['added_lines']} -{r['removed_lines']} "
        f"| risk={r['risk']} | decision={r['decision']} | {r['reason']}"
    )
md.append("")
md.append("## Safety")
md.append("- No file restored")
md.append("- No file moved")
md.append("- No file deleted")
md.append("- No runtime modified")
md.append("- Dry-run only")
md.append("")
md.append("## Next")
if summary["p19p39_allowed"]:
    md.append("P19P39 ADAPTER-ONLY SHADOW WIRING")
else:
    md.append("P19P38-L RUNTIME DIFF CLEAN DECISION")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
