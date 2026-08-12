import json, os, re, hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

OUT = Path(os.environ["P5_OUT"])
BRAIN = Path(os.environ["P5_BRAIN"])
SCANS = [Path(x) for x in os.environ["P5_SCANS"].split("|") if x]
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = {
 "AGENTS": ["agent/", "agents/", "_agent", "agent_", "swarm", "worker", "persistent_agent", "agent_orchestrator"],
 "MULTI_AGENT": ["multi_agent", "multiagent", "swarm", "federation", "council", "multi_mind", "multi_plan", "agent_bid"],
 "HIERARCHICAL_PLANNING": ["hierarchical_planner", "hplanner", "neural_long_planner", "internal_planner", "goal_decomposition", "task_tree", "route_hplanner", "route_neural_planner", "route_talk_planner", "hierarchical_planner_step449"],
 "COGNITIVE_CONTROL": ["cognitive_control", "metacognition", "meta_reasoning", "control_loop", "cognitive_loop", "oversight", "self_monitor", "self_correction", "executive_control", "cognitive_governor"],
 "ORCHESTRATION": ["orchestrator", "orchestration", "route_orchestrator", "internal_state_orchestrator"]
}
NOISE = ["node_modules", "__pycache__", ".venv", "site-packages", "android-sdk", "babel_runtime", "cpython-312.pyc"]

def read(p):
    try: return p.read_text(encoding="utf-8", errors="ignore")
    except Exception: return ""

def load_json(p):
    try: return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception: return []

def is_noise(s):
    x=s.lower()
    return any(n in x for n in NOISE)

def classify(line):
    low=line.lower()
    return sorted([cap for cap,keys in TARGETS.items() if any(k in low for k in keys)])

brain_gap = load_json(BRAIN / "MIND_GAP_MATRIX.json")
brain_status = load_json(BRAIN / "MIND_CAPABILITY_STATUS_MATRIX.json")
brain_unconnected = load_json(BRAIN / "MIND_UNCONNECTED_CAPABILITY_LEDGER.json")

records = {}
total = 0

for sf in SCANS:
    text = read(sf)
    for raw in text.splitlines():
        total += 1
        line = raw.strip().replace("\\", "/")
        if not line or line.startswith("SCANNED:"):
            continue
        caps = classify(line)
        if not caps:
            continue
        h = hashlib.sha1((str(sf)+"|"+line).encode("utf-8", errors="ignore")).hexdigest()
        records[h] = {
            "source_scan": str(sf),
            "path": line,
            "capabilities": caps,
            "is_noise": is_noise(line)
        }

records = list(records.values())
by_cap = defaultdict(list)
for r in records:
    for c in r["capabilities"]:
        by_cap[c].append(r)

summary = []
for cap in ["HIERARCHICAL_PLANNING","COGNITIVE_CONTROL","AGENTS","MULTI_AGENT","ORCHESTRATION"]:
    all_items = by_cap.get(cap, [])
    clean = [x for x in all_items if not x["is_noise"]]
    summary.append({
        "capability": cap,
        "drive_hits_total": len(all_items),
        "drive_hits_clean": len(clean),
        "top_candidates": clean[:100],
        "brain_gap": [x for x in brain_gap if x.get("capability") == cap][:1],
        "brain_status": [x for x in brain_status if x.get("capability") == cap][:1],
        "decision": (
            "DEEP_AUDIT_FIRST" if cap == "HIERARCHICAL_PLANNING" and clean else
            "DEEP_AUDIT_MISSING_CAPABILITY" if cap == "COGNITIVE_CONTROL" and clean else
            "RECONCILE_DISCONNECTED_SUBSYSTEM" if cap in ["AGENTS","MULTI_AGENT"] and clean else
            "REFERENCE_REVIEW" if clean else
            "NO_ACTION"
        )
    })

important_re = re.compile(
    r"(hierarchical_planner|neural_long_planner|internal_planner|route_hplanner|route_neural_planner|"
    r"route_talk_planner|hierarchical_planner_step449|route_internal_state_orchestrator|route_orchestrator|"
    r"auto_evo_pr_planner|auto_evo_module_growth_planner|social_relationship_orchestrator|"
    r"dev_step_planner_agent|agent/planner|cognitive_control|metacognition|cognitive_loop|oversight|"
    r"multi_agent|multi_mind|swarm|federation|council)",
    re.I
)
important = [r for r in records if important_re.search(r["path"]) and not r["is_noise"]]

final = {
    "STATUS": "P5_12_COMPLETE",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "scan_files_count": len(SCANS),
    "scan_lines_total": total,
    "matched_records": len(records),
    "important_candidates": len(important),
    "verdict": {
        "hierarchical_planning_gap": "CONFIRMED_FOR_DEEP_AUDIT" if by_cap.get("HIERARCHICAL_PLANNING") else "NOT_CONFIRMED",
        "agents_gap": "CONFIRMED_DISCONNECTED_OR_UNRECONCILED" if by_cap.get("AGENTS") else "NOT_CONFIRMED",
        "multi_agent_gap": "CONFIRMED_DISCONNECTED_OR_UNRECONCILED" if by_cap.get("MULTI_AGENT") else "NOT_CONFIRMED",
        "cognitive_control_gap": "SEARCH_HIT_REVIEW_REQUIRED" if by_cap.get("COGNITIVE_CONTROL") else "STILL_MISSING"
    },
    "code_changed": False,
    "build_allowed": False,
    "integration_allowed": False,
    "move_allowed": False,
    "archive_allowed": False
}

artifacts = {
    "P5_12_INPUT_SCAN_FILES.json": [str(x) for x in SCANS],
    "DRIVE_SCAN_MATCHED_CAPABILITIES.json": records,
    "DRIVE_SCAN_CAPABILITY_SUMMARY.json": summary,
    "DRIVE_SCAN_IMPORTANT_CANDIDATES.json": important,
    "BRAIN_MAP_GAP_REFERENCE.json": brain_gap,
    "BRAIN_MAP_STATUS_REFERENCE.json": brain_status,
    "BRAIN_MAP_UNCONNECTED_REFERENCE.json": brain_unconnected,
    "P5_12_FINAL_RECONCILIATION_VERDICT.json": final
}

for name,data in artifacts.items():
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

(OUT / "P5_12_FINAL_RECONCILIATION_VERDICT.md").write_text(
    "# P5.12 FINAL VERDICT\n\n```json\n" + json.dumps(final, ensure_ascii=False, indent=2) + "\n```\n",
    encoding="utf-8"
)

print(json.dumps(final, ensure_ascii=False, indent=2))
