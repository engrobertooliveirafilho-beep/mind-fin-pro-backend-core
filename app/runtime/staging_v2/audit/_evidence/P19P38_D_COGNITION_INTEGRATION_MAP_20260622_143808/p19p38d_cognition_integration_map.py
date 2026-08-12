from pathlib import Path
import json
import os
import re
from datetime import datetime, timezone

ROOT = Path.cwd()
OUT = Path(os.environ["P19P38D_EVID"])
OUT.mkdir(parents=True, exist_ok=True)

MODULES = [
    {
        "id": "safe_recovery_adapter",
        "path": "app/companionship/safe_recovery_adapter.py",
        "role": "central_context_collector",
        "expected_mode": "shadow_plus_gated_live",
        "criticality": "HIGH",
    },
    {
        "id": "relationship_memory_store",
        "path": "app/companionship/relationship_memory_store.py",
        "role": "relationship_memory_writer_reader",
        "expected_mode": "shadow",
        "criticality": "HIGH",
    },
    {
        "id": "long_term_goal_tracker",
        "path": "app/companionship/long_term_goal_tracker.py",
        "role": "goal_tracking_writer_reader",
        "expected_mode": "shadow",
        "criticality": "HIGH",
    },
    {
        "id": "digital_twin_real",
        "path": "app/companionship/digital_twin_real.py",
        "role": "user_model_snapshot_builder",
        "expected_mode": "shadow",
        "criticality": "HIGH",
    },
    {
        "id": "behavior_modeling",
        "path": "app/companionship/behavior_modeling.py",
        "role": "behavior_signal_inference",
        "expected_mode": "shadow",
        "criticality": "MEDIUM",
    },
    {
        "id": "emotional_continuity_real",
        "path": "app/companionship/emotional_continuity_real.py",
        "role": "emotional_signal_continuity_without_diagnosis",
        "expected_mode": "shadow",
        "criticality": "MEDIUM",
    },
    {
        "id": "long_term_memory_real",
        "path": "app/companionship/long_term_memory_real.py",
        "role": "stable_memory_consolidation",
        "expected_mode": "shadow",
        "criticality": "HIGH",
    },
    {
        "id": "self_reflection_engine",
        "path": "app/companionship/self_reflection_engine.py",
        "role": "internal_state_quality_assessment",
        "expected_mode": "shadow",
        "criticality": "HIGH",
    },
    {
        "id": "live_cognition_gated",
        "path": "app/companionship/live_cognition_gated.py",
        "role": "feature_flagged_live_cognition_decision",
        "expected_mode": "gated_live",
        "criticality": "CRITICAL",
    },
    {
        "id": "whatsapp_runtime",
        "path": "app/api/whatsapp.py",
        "role": "production_message_entrypoint",
        "expected_mode": "live",
        "criticality": "CRITICAL",
    },
    {
        "id": "cognitive_pipeline",
        "path": "app/runtime/cognitive_pipeline.py",
        "role": "runtime_cognition_pipeline",
        "expected_mode": "live",
        "criticality": "CRITICAL",
    },
]

EXPECTED_EDGES = [
    ["safe_recovery_adapter", "relationship_memory_store", "writes_reads_profile"],
    ["safe_recovery_adapter", "long_term_goal_tracker", "writes_goal_shadow"],
    ["relationship_memory_store", "long_term_goal_tracker", "feeds_goals"],
    ["relationship_memory_store", "digital_twin_real", "feeds_profile"],
    ["long_term_goal_tracker", "digital_twin_real", "feeds_goal_objects"],
    ["digital_twin_real", "long_term_memory_real", "feeds_stable_profile"],
    ["behavior_modeling", "digital_twin_real", "feeds_behavior_signals"],
    ["emotional_continuity_real", "self_reflection_engine", "feeds_emotional_state"],
    ["long_term_memory_real", "self_reflection_engine", "feeds_memory_quality"],
    ["self_reflection_engine", "live_cognition_gated", "feeds_readiness"],
    ["digital_twin_real", "live_cognition_gated", "required_layer"],
    ["behavior_modeling", "live_cognition_gated", "required_layer"],
    ["emotional_continuity_real", "live_cognition_gated", "required_layer"],
    ["long_term_memory_real", "live_cognition_gated", "required_layer"],
    ["live_cognition_gated", "safe_recovery_adapter", "should_be_attached"],
    ["safe_recovery_adapter", "whatsapp_runtime", "runtime_context_candidate"],
    ["safe_recovery_adapter", "cognitive_pipeline", "runtime_context_candidate"],
]

def read(path):
    p = ROOT / path
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def grep_refs(token):
    refs = []
    for base in ["app", "tests"]:
        root = ROOT / base
        if not root.exists():
            continue
        for p in root.rglob("*.py"):
            rel = p.relative_to(ROOT).as_posix()
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if token in txt:
                refs.append(rel)
    return sorted(set(refs))

def extract_flags(text):
    flags = sorted(set(re.findall(r'P19P[0-9A-Z_]+|P19P37_[A-Z0-9_]+|P19P38[A-Z_]+', text)))
    envs = sorted(set(re.findall(r'os\.getenv\(["\']([^"\']+)["\']', text)))
    return sorted(set(flags + envs))

def extract_context_keys(text):
    return sorted(set(re.findall(r'p19p[0-9a-z_]+', text.lower())))

nodes = []

for m in MODULES:
    text = read(m["path"])
    exists = bool(text)
    refs = grep_refs(Path(m["path"]).stem)
    flags = extract_flags(text)
    keys = extract_context_keys(text)

    status = "MISSING"
    if exists:
        if "SHADOW_ONLY" in text and "LIVE_GATED" in text:
            status = "SHADOW_AND_GATED"
        elif "SHADOW_ONLY" in text:
            status = "SHADOW_ONLY"
        elif "live" in m["expected_mode"].lower():
            status = "LIVE_OR_RUNTIME"
        else:
            status = "PRESENT"

    nodes.append({
        **m,
        "exists": exists,
        "size": (ROOT / m["path"]).stat().st_size if exists else 0,
        "status": status,
        "references_total": len(refs),
        "references": refs[:40],
        "feature_flags_or_markers": flags,
        "context_keys": keys[:80],
    })

edges = []
for source, target, relation in EXPECTED_EDGES:
    s_node = next((x for x in nodes if x["id"] == source), None)
    t_node = next((x for x in nodes if x["id"] == target), None)

    s_exists = bool(s_node and s_node["exists"])
    t_exists = bool(t_node and t_node["exists"])

    evidence = []
    if s_exists and t_node:
        s_text = read(s_node["path"])
        if Path(t_node["path"]).stem in s_text or target in s_text:
            evidence.append("source_mentions_target")
    if t_exists and s_node:
        t_text = read(t_node["path"])
        if Path(s_node["path"]).stem in t_text or source in t_text:
            evidence.append("target_mentions_source")

    edge_status = "MISSING_NODE"
    if s_exists and t_exists:
        edge_status = "EVIDENCED" if evidence else "EXPECTED_NOT_WIRED"

    edges.append({
        "source": source,
        "target": target,
        "relation": relation,
        "status": edge_status,
        "evidence": evidence,
    })

missing_nodes = [n for n in nodes if not n["exists"]]
shadow_nodes = [n for n in nodes if n["status"] in ["SHADOW_ONLY", "SHADOW_AND_GATED"]]
critical_missing = [n for n in missing_nodes if n["criticality"] in ["HIGH", "CRITICAL"]]
expected_not_wired = [e for e in edges if e["status"] == "EXPECTED_NOT_WIRED"]

promotion_candidates = []
blocked_candidates = []

for n in nodes:
    if not n["exists"]:
        blocked_candidates.append({
            "id": n["id"],
            "reason": "missing module",
            "next_action": "create_or_restore_module",
        })
    elif n["criticality"] in ["HIGH", "CRITICAL"] and n["status"] == "SHADOW_ONLY":
        promotion_candidates.append({
            "id": n["id"],
            "reason": "high-value shadow module present",
            "next_action": "consider canary wiring after runtime audit",
        })

summary = {
    "mission": "P19P38_D_COGNITION_INTEGRATION_MAP",
    "status": "AUDIT_ONLY_PASS",
    "runtime_modified": False,
    "files_moved": False,
    "files_deleted": False,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "nodes_total": len(nodes),
    "nodes_missing": len(missing_nodes),
    "critical_missing": len(critical_missing),
    "edges_total": len(edges),
    "edges_evidenced": sum(1 for e in edges if e["status"] == "EVIDENCED"),
    "edges_expected_not_wired": len(expected_not_wired),
    "promotion_candidates": len(promotion_candidates),
    "blocked_candidates": len(blocked_candidates),
}

graph = {
    "summary": summary,
    "nodes": nodes,
    "edges": edges,
    "promotion_candidates": promotion_candidates,
    "blocked_candidates": blocked_candidates,
}

(OUT / "cognition_integration_graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

csv = ["source,target,relation,status,evidence"]
for e in edges:
    csv.append(f'{e["source"]},{e["target"]},{e["relation"]},{e["status"]},"{";".join(e["evidence"])}"')
(OUT / "cognition_edges.csv").write_text("\n".join(csv), encoding="utf-8")

md = []
md.append("# P19P38-D Cognition Integration Map")
md.append("")
md.append(f"Status: {summary['status']}")
md.append(f"Generated: {summary['generated_at']}")
md.append("")
md.append("## Summary")
for k, v in summary.items():
    if k not in ["mission", "status", "generated_at"]:
        md.append(f"- {k}: {v}")
md.append("")
md.append("## Nodes")
for n in nodes:
    md.append(f"- {n['id']} | exists={n['exists']} | status={n['status']} | refs={n['references_total']} | criticality={n['criticality']}")
md.append("")
md.append("## Missing Critical Nodes")
for n in critical_missing:
    md.append(f"- {n['id']} | {n['path']} | role={n['role']}")
md.append("")
md.append("## Expected Edges Not Wired")
for e in expected_not_wired:
    md.append(f"- {e['source']} -> {e['target']} | {e['relation']}")
md.append("")
md.append("## Promotion Candidates")
for c in promotion_candidates:
    md.append(f"- {c['id']} | {c['reason']} | {c['next_action']}")
md.append("")
md.append("## Blocked Candidates")
for c in blocked_candidates:
    md.append(f"- {c['id']} | {c['reason']} | {c['next_action']}")
md.append("")
md.append("## Safety")
md.append("- No files moved")
md.append("- No files deleted")
md.append("- No runtime modified")
md.append("- Integration map only")
md.append("")
md.append("## Next")
md.append("P19P37E/P19P37F completion if missing, then P19P38-E Runtime Wiring Audit")

(OUT / "REPORT.md").write_text("\n".join(md), encoding="utf-8")

print(json.dumps(summary, ensure_ascii=False, indent=2))
