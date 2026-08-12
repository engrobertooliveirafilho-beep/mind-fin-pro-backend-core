from pathlib import Path
import json
import os
import re
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38F_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

CANDIDATES = [
    ("memory_fusion_live", "app/companionship/safe_recovery_adapter.py", "HIGH"),
    ("relationship_memory", "app/companionship/relationship_memory_store.py", "HIGH"),
    ("long_term_goal_tracker", "app/companionship/long_term_goal_tracker.py", "HIGH"),
    ("digital_twin_real", "app/companionship/digital_twin_real.py", "HIGH"),
    ("behavior_modeling", "app/companionship/behavior_modeling.py", "MEDIUM"),
    ("emotional_continuity_real", "app/companionship/emotional_continuity_real.py", "MEDIUM"),
    ("long_term_memory_real", "app/companionship/long_term_memory_real.py", "HIGH"),
    ("self_reflection_engine", "app/companionship/self_reflection_engine.py", "HIGH"),
    ("live_cognition_gated", "app/companionship/live_cognition_gated.py", "CRITICAL"),
]

def read(path):
    p = ROOT / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

def tests_for(token):
    tests = []
    test_root = ROOT / "tests"
    if not test_root.exists():
        return tests
    for p in test_root.rglob("test*.py"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if token in txt or token.replace("_", "") in txt.replace("_", ""):
            tests.append(p.relative_to(ROOT).as_posix())
    return sorted(set(tests))

def has_feature_flag(text):
    return "os.getenv" in text or "ENABLED" in text or "FEATURE" in text

def has_shadow(text):
    return "SHADOW_ONLY" in text or "shadow" in text.lower()

def has_live_gate(text):
    return "LIVE_GATED" in text or "live_allowed" in text or "response_impact" in text

rows = []

for name, path, risk in CANDIDATES:
    txt = read(path)
    exists = bool(txt)
    test_refs = tests_for(name)
    flags = has_feature_flag(txt)
    shadow = has_shadow(txt)
    live_gate = has_live_gate(txt)
    functions = re.findall(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", txt, flags=re.M)

    status = "BLOCKED"
    reason = []

    if not exists:
        status = "BLOCKED"
        reason.append("module_missing")
    elif not test_refs:
        status = "SHADOW_ONLY"
        reason.append("no_direct_tests_found")
    elif shadow and flags and live_gate:
        status = "CANARY_READY"
        reason.append("shadow_feature_flag_live_gate_present")
    elif shadow and flags:
        status = "CANARY_READY"
        reason.append("shadow_and_feature_flag_present")
    elif shadow:
        status = "SHADOW_ONLY"
        reason.append("shadow_only_no_feature_flag")
    else:
        status = "SHADOW_ONLY"
        reason.append("present_but_no_runtime_gate")

    if risk == "CRITICAL" and status == "CANARY_READY":
        reason.append("critical_requires_runtime_wiring_audit_before_production")

    rows.append({
        "candidate": name,
        "path": path,
        "exists": exists,
        "risk": risk,
        "tests": test_refs,
        "test_count": len(test_refs),
        "has_feature_flag": flags,
        "has_shadow": shadow,
        "has_live_gate": live_gate,
        "functions": functions,
        "promotion_status": status,
        "reason": reason,
        "next_action": (
            "create_or_restore_module" if not exists else
            "wire_adapter_shadow_only" if status == "CANARY_READY" else
            "add_tests_and_feature_flag" if status == "SHADOW_ONLY" else
            "manual_review"
        )
    })

counts = {}
for r in rows:
    counts[r["promotion_status"]] = counts.get(r["promotion_status"], 0) + 1

summary = {
    "mission": "P19P38_F_PRODUCTION_CANDIDATE_MAP",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "candidates_total": len(rows),
    "counts": counts,
    "production_ready": counts.get("PRODUCTION_READY", 0),
    "canary_ready": counts.get("CANARY_READY", 0),
    "blocked": counts.get("BLOCKED", 0),
}

(OUT / "production_candidate_map.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

csv = ["candidate,path,exists,risk,test_count,has_feature_flag,has_shadow,has_live_gate,promotion_status,next_action"]
for r in rows:
    csv.append(f'{r["candidate"]},{r["path"]},{r["exists"]},{r["risk"]},{r["test_count"]},{r["has_feature_flag"]},{r["has_shadow"]},{r["has_live_gate"]},{r["promotion_status"]},{r["next_action"]}')
(OUT / "production_candidate_map.csv").write_text("\n".join(csv), encoding="utf-8")

md = []
md.append("# P19P38-F Production Candidate Map")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## Candidates")
for r in rows:
    md.append(f"- {r['candidate']} | {r['promotion_status']} | risk={r['risk']} | tests={r['test_count']} | next={r['next_action']}")
md.append("")
md.append("## Rule")
md.append("- No runtime patch")
md.append("- No WhatsApp patch")
md.append("- No cognitive_pipeline patch")
md.append("- Candidate map only")
md.append("")
md.append("## Next")
md.append("P19P39 ADAPTER-ONLY SHADOW WIRING")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
