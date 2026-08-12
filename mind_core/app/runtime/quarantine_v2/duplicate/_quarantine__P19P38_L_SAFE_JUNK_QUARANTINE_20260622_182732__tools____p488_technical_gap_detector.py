import json
from pathlib import Path
from datetime import datetime, timezone

OUT1 = Path("runtime/technical_gaps/technical_gap_report.json")
OUT2 = Path("runtime/technical_gaps/gap_resolution_backlog.json")

SOURCES = [
    "runtime/capability_map/absorbed_vs_pending_map.json",
    "runtime/knowledge_graph/drive_knowledge_graph.json",
    "runtime/orphan_recovery/orphan_recovery_plan.json",
    "runtime/orphan_recovery/adapter_recovery_plan.json",
    "runtime/capability_merge/capability_merge_report.json",
    "runtime/reconstruction/capability_reconstruction_plan.json",
]

DESIRED = [
    "retrieval",
    "memory",
    "capability_registry",
    "drive_absorption",
    "knowledge_extraction",
    "runtime_review_queue",
    "auto_prioritization",
    "safe_code_generation_gate",
    "capability_reconstruction",
    "drive_knowledge_graph",
    "orphan_recovery",
    "capability_merge",
    "technical_gap_detector",
    "full_repository_intelligence",
    "sovereign_certification"
]

def load(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_error": str(e)}

blob = ""
source_status = {}

for src in SOURCES:
    data = load(src)
    source_status[src] = data is not None
    if data is not None:
        blob += json.dumps(data, ensure_ascii=False).lower() + "\n"

existing = []
missing = []

for cap in DESIRED:
    probe = cap.replace("_", " ")
    compact = cap.replace("_", "")
    if cap.lower() in blob or probe in blob or compact in blob.replace("_", "").replace(" ", ""):
        existing.append(cap)
    else:
        missing.append(cap)

known_gap_items = [
    {
        "gap_id": "GAP-FRI-001",
        "capability": "full_repository_intelligence",
        "severity": "CRITICAL",
        "status": "OPEN",
        "reason": "P4.89 ainda não executado.",
        "required_output": "runtime/repository_intelligence/full_repository_intelligence_report.json"
    },
    {
        "gap_id": "GAP-SOV-001",
        "capability": "sovereign_certification",
        "severity": "CRITICAL",
        "status": "OPEN",
        "reason": "P4.90 depende de P4.88 e P4.89 certificados.",
        "required_output": "runtime/certification/sovereign_technical_capacity_certification.json"
    }
]

for cap in missing:
    if cap not in ["full_repository_intelligence", "sovereign_certification"]:
        known_gap_items.append({
            "gap_id": "GAP-" + cap.upper().replace("_", "-"),
            "capability": cap,
            "severity": "HIGH",
            "status": "OPEN",
            "reason": "Capacidade desejada não encontrada nos artefatos consolidados.",
            "required_output": None
        })

backlog = []
for idx, gap in enumerate(known_gap_items, start=1):
    backlog.append({
        "backlog_id": f"P4.88-B{idx:03d}",
        "gap_id": gap["gap_id"],
        "capability": gap["capability"],
        "priority": "P0" if gap["severity"] == "CRITICAL" else "P1",
        "approval_status": "PENDING_APPROVAL",
        "execution_status": "BLOCKED_BY_P4.83_GATE",
        "mode": "PLAN_ONLY",
        "recommended_action": "create_or_complete_capability_mission",
        "required_output": gap.get("required_output")
    })

report = {
    "milestone": "P4.88 COMPLETE",
    "engine": "TECHNICAL_GAP_DETECTOR",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY",
    "governance": "P4.83_ENFORCED",
    "sources": source_status,
    "desired_capabilities": DESIRED,
    "existing_capabilities": existing,
    "missing_capabilities": missing,
    "gaps_count": len(known_gap_items),
    "gaps": known_gap_items,
    "next": "P4.89 FULL REPOSITORY INTELLIGENCE"
}

resolution = {
    "milestone": "P4.88 COMPLETE",
    "backlog": "GAP_RESOLUTION_BACKLOG",
    "mode": "PLAN_ONLY",
    "automatic_execution": "FORBIDDEN",
    "approval_required": True,
    "items_count": len(backlog),
    "items": backlog
}

OUT1.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
OUT2.write_text(json.dumps(resolution, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.88 COMPLETE",
    "desired": len(DESIRED),
    "existing": len(existing),
    "missing": len(missing),
    "gaps": len(known_gap_items),
    "mode": "PLAN_ONLY",
    "next": "P4.89 FULL REPOSITORY INTELLIGENCE"
}, indent=2, ensure_ascii=False))
