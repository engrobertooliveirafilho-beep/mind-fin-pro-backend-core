from pathlib import Path
import json
import os
import subprocess
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38J_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    "app/api/whatsapp.py",
    "app/runtime/cognitive_pipeline.py",
]

MISSION_HINTS = {
    "P19P36": ["p19p36", "memory_fusion", "relationship_memory", "long_term_goal"],
    "P19P37": ["p19p37", "digital_twin", "behavior", "emotional_continuity", "self_reflection", "live_cognition"],
    "P19P38": ["p19p38", "audit", "forensic", "worktree", "candidate"],
    "P4_FIX": ["fix11k", "p4_", "normalize", "semantic_guard", "reply_lock"],
    "WHATSAPP_RUNTIME": ["webhook", "twilio", "body", "from", "messagesid", "twiml", "response"],
    "COGNITIVE_PIPELINE": ["pipeline", "cognitive", "route", "final_output", "guard"],
}

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

def classify_origin(text):
    lower = text.lower()
    hits = {}
    for group, terms in MISSION_HINTS.items():
        count = sum(1 for t in terms if t in lower)
        if count:
            hits[group] = count
    if not hits:
        return "UNKNOWN", hits
    return max(hits, key=hits.get), hits

def classify_action(path, text, origin):
    lower = text.lower()

    added = [x for x in text.splitlines() if x.startswith("+") and not x.startswith("+++")]
    removed = [x for x in text.splitlines() if x.startswith("-") and not x.startswith("---")]

    runtime_terms = ["webhook", "twilio", "response", "return", "pipeline", "guard", "route"]
    cognition_terms = ["shadow", "memory", "digital_twin", "self_reflection", "live_cognition", "safe_recovery_adapter"]
    telemetry_terms = ["telemetry", "audit", "trace", "ledger"]

    runtime_hit = any(t in lower for t in runtime_terms)
    cognition_hit = any(t in lower for t in cognition_terms)
    telemetry_hit = any(t in lower for t in telemetry_terms)

    if runtime_hit and removed:
        return "REVIEW_LINE_BY_LINE", "runtime behavior changed with removals"
    if runtime_hit and not cognition_hit:
        return "REVIEW_LINE_BY_LINE", "runtime path modified"
    if cognition_hit and telemetry_hit and not removed:
        return "KEEP_CANDIDATE_SEPARATE_COMMIT", "cognition/telemetry additive"
    if cognition_hit and not removed:
        return "ISOLATE_COGNITION_PATCH", "cognition additive but needs tests"
    if telemetry_hit and not removed:
        return "KEEP_CANDIDATE_TELEMETRY", "telemetry additive"
    return "UNKNOWN_MANUAL_DECISION", "insufficient signal"

reviews = []

for path in TARGETS:
    diff = diff_for(path)
    hunks = split_hunks(diff)

    for idx, lines in enumerate(hunks, start=1):
        text = "\n".join(lines)
        origin, origin_hits = classify_origin(text)
        action, reason = classify_action(path, text, origin)

        added = [x for x in lines if x.startswith("+") and not x.startswith("+++")]
        removed = [x for x in lines if x.startswith("-") and not x.startswith("---")]

        review = {
            "path": path,
            "hunk_index": idx,
            "header": lines[0] if lines else "",
            "added_lines": len(added),
            "removed_lines": len(removed),
            "origin_guess": origin,
            "origin_hits": origin_hits,
            "recommended_action": action,
            "reason": reason,
            "preview": "\n".join(lines[:80]),
        }

        reviews.append(review)

        hunk_file = OUT / f"HUNK_{path.replace('/', '__')}_{idx}.diff"
        hunk_file.write_text(text, encoding="utf-8")

counts = {}
for r in reviews:
    counts[r["recommended_action"]] = counts.get(r["recommended_action"], 0) + 1

blocking_actions = {"REVIEW_LINE_BY_LINE", "UNKNOWN_MANUAL_DECISION", "ISOLATE_COGNITION_PATCH"}
blocking = [r for r in reviews if r["recommended_action"] in blocking_actions]

summary = {
    "mission": "P19P38_J_CRITICAL_RUNTIME_MANUAL_REVIEW",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "hunks_total": len(reviews),
    "blocking_hunks": len(blocking),
    "p19p39_allowed": len(blocking) == 0,
    "counts": counts,
}

next_action = "P19P38-K critical diff resolution executor" if blocking else "P19P39 adapter-only shadow wiring"

(OUT / "manual_hunk_reviews.json").write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

md = []
md.append("# P19P38-J Critical Runtime Manual Review")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## Hunk Decisions")
for r in reviews:
    md.append(f"- {r['path']} H{r['hunk_index']} | +{r['added_lines']} -{r['removed_lines']} | origin={r['origin_guess']} | action={r['recommended_action']} | {r['reason']}")
md.append("")
md.append("## Blocking Hunks")
for r in blocking:
    md.append(f"- {r['path']} H{r['hunk_index']} | action={r['recommended_action']} | reason={r['reason']}")
md.append("")
md.append("## Safety")
md.append("- No file restored")
md.append("- No file moved")
md.append("- No file deleted")
md.append("- No runtime modified")
md.append("- Manual classification only")
md.append("")
md.append("## Next")
md.append(next_action)

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
