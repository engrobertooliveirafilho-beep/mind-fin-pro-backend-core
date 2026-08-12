import json, os, re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone

OUT = Path(os.environ["P5_OUT"])
P512 = Path(os.environ["P5_12"])
OUT.mkdir(parents=True, exist_ok=True)

def load(name):
    p = P512 / name
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []

important = load("DRIVE_SCAN_IMPORTANT_CANDIDATES.json")
summary = load("DRIVE_SCAN_CAPABILITY_SUMMARY.json")
matched = load("DRIVE_SCAN_MATCHED_CAPABILITIES.json")

NOISE = [
    "node_modules", "__pycache__", ".venv", "site-packages", "android-sdk",
    "babel_runtime", "cpython-312.pyc", ".map.txt", "package-lock", "yarn.lock"
]

PRIORITY_TERMS = {
    "HIERARCHICAL_PLANNING": [
        "hierarchical_planner", "hierarchical_planner_step449", "neural_long_planner",
        "internal_planner", "goal_decomposition", "task_tree", "route_hplanner",
        "route_neural_planner", "route_talk_planner"
    ],
    "COGNITIVE_CONTROL": [
        "cognitive_control", "metacognition", "meta_reasoning", "control_loop",
        "cognitive_loop", "oversight", "self_monitor", "self_correction",
        "executive_control", "cognitive_governor"
    ],
    "AGENTS": [
        "agent_orchestrator", "persistent_agent_worker", "browser_fleet_runtime",
        "business_runtime", "task_engine", "dev_step_planner_agent",
        "agent/planner", "agent_", "agents/"
    ],
    "MULTI_AGENT": [
        "multi_agent", "multiagent", "multi_mind", "multi_plan", "swarm",
        "federation", "council", "agent_bid", "task_market"
    ],
    "ORCHESTRATION": [
        "orchestrator", "route_orchestrator", "internal_state_orchestrator"
    ]
}

def is_noise(path):
    low = path.lower()
    return any(n in low for n in NOISE)

def score_record(r):
    path = r.get("path","")
    low = path.lower()
    caps = r.get("capabilities", [])
    score = 0
    reasons = []

    if is_noise(path):
        score -= 100
        reasons.append("NOISE")

    if "tests/" in low or "/tests/" in low:
        score -= 10
        reasons.append("TEST_ONLY")

    if "/app/" in low or "_app_" in low:
        score += 20
        reasons.append("APP_CODE")

    if path.endswith(".py") or ".py.txt" in low:
        score += 15
        reasons.append("PYTHON_SOURCE")

    if "route_" in low or "/routes" in low or "/api/" in low:
        score += 8
        reasons.append("ROUTE_OR_API")

    for cap in caps:
        for term in PRIORITY_TERMS.get(cap, []):
            if term.lower() in low:
                score += 25
                reasons.append(f"TERM:{term}")

    if "hierarchical_planner_step449" in low:
        score += 60
        reasons.append("KNOWN_DIAMOND_GAP")

    if "app/planning/" in low or "_app_planning_" in low:
        score += 40
        reasons.append("PLANNING_MODULE")

    if "cognitive_control" in low or "metacognition" in low or "oversight" in low:
        score += 50
        reasons.append("COGNITIVE_CONTROL_SIGNAL")

    if "multi_agent" in low or "swarm" in low:
        score += 30
        reasons.append("MULTI_AGENT_SIGNAL")

    return score, sorted(set(reasons))

ranked = []
for r in important:
    score, reasons = score_record(r)
    ranked.append({**r, "score": score, "reasons": reasons})

ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

by_cap = defaultdict(list)
for r in ranked:
    for c in r.get("capabilities", []):
        by_cap[c].append(r)

decisions = []
for cap in ["HIERARCHICAL_PLANNING", "COGNITIVE_CONTROL", "AGENTS", "MULTI_AGENT", "ORCHESTRATION"]:
    items = [x for x in by_cap.get(cap, []) if x["score"] > 0]
    top = items[:50]

    if cap == "HIERARCHICAL_PLANNING":
        decision = "INTEGRAR_FUTURAMENTE_OU_RECONCILIAR_APOS_LEITURA_DE_CODIGO"
        priority = "CRITICAL"
    elif cap == "COGNITIVE_CONTROL":
        decision = "DEEP_SEARCH_REQUIRED"
        priority = "HIGH"
    elif cap in ["AGENTS", "MULTI_AGENT"]:
        decision = "RECONCILIAR_SUBSISTEMA_DESCONECTADO"
        priority = "HIGH"
    else:
        decision = "REFERENCIA"
        priority = "MEDIUM"

    decisions.append({
        "capability": cap,
        "candidate_count_positive": len(items),
        "priority": priority,
        "decision": decision,
        "top_candidates": top
    })

# Reduzir candidatos canônicos por assinatura de nome
canonical = []
seen = set()
for r in ranked:
    if r["score"] <= 0:
        continue
    p = r["path"]
    key = re.sub(r"^\d+[_\d]*", "", p.lower())
    key = re.sub(r".*app[_/]", "app/", key)
    key = re.sub(r".*services[_/]", "services/", key)
    key = re.sub(r"\.txt$", "", key)
    if key in seen:
        continue
    seen.add(key)
    canonical.append(r)
    if len(canonical) >= 300:
        break

final = {
    "STATUS": "P5_13_COMPLETE",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "source_p512": str(P512),
    "important_input_count": len(important),
    "ranked_positive_count": len([x for x in ranked if x["score"] > 0]),
    "canonical_candidate_count": len(canonical),
    "top_decisions": decisions,
    "locks": {
        "build_allowed": False,
        "integration_allowed": False,
        "move_allowed": False,
        "archive_allowed": False,
        "code_changed": False
    },
    "next_required_action": "P5.14_OPEN_TOP_CANONICAL_CANDIDATES_AND_COMPARE_CODE"
}

artifacts = {
    "P5_13_RANKED_IMPORTANT_CANDIDATES.json": ranked,
    "P5_13_CANONICAL_CANDIDATES_TOP300.json": canonical,
    "P5_13_CAPABILITY_DECISION_MATRIX.json": decisions,
    "P5_13_FINAL_DEEP_AUDIT_LEDGER.json": final
}

for name, data in artifacts.items():
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

(OUT / "P5_13_FINAL_DEEP_AUDIT_LEDGER.md").write_text(
    "# P5.13 FINAL DEEP AUDIT LEDGER\n\n```json\n" +
    json.dumps(final, ensure_ascii=False, indent=2) +
    "\n```\n",
    encoding="utf-8"
)

print(json.dumps(final, ensure_ascii=False, indent=2))
