import json
from pathlib import Path
from datetime import datetime, timezone

PRIORITY = Path("runtime/prioritization/runtime_prioritized_queue.json")
GATE = Path("runtime/governance/safe_code_generation_gate.json")
OUT = Path("runtime/reconstruction/capability_reconstruction_plan.json")

def infer_targets(text):
    low = text.lower()
    files = []
    tests = []
    deps = []

    if "whatsapp" in low or "runtime" in low:
        files += ["app/api/whatsapp.py", "app/runtime/cognitive_pipeline.py"]
        tests += ["tests/test_whatsapp_positive_feedback.py", "tests/test_eldora_whatsapp_cognitive_pipeline.py"]
        deps += ["runtime/governance/safe_code_generation_gate.json"]

    if "knowledge" in low or "graph" in low or "drive" in low:
        files += ["app/runtime/knowledge_extraction_engine.py", "runtime/capability_map/absorbed_vs_pending_map.json"]
        tests += ["tests/test_p479_knowledge_extraction_engine.py"]
        deps += ["runtime/capacity_audit/project_state_audit.json"]

    if "capability" in low or "orphan" in low or "adapter" in low:
        files += ["app/runtime/universal_capability_registry.json"]
        tests += ["tests/test_p482_runtime_prioritization.py"]
        deps += ["runtime/review_queue/runtime_review_queue.json"]

    if "governance" in low or "approval" in low or "gate" in low:
        files += ["runtime/governance/safe_code_generation_gate.json", "runtime/approval_contracts/mission_approval_contract.json"]
        tests += ["tests/test_p483_safe_code_generation_gate.py"]
        deps += ["runtime/execution_locks/auto_execution_lock.json"]

    return sorted(set(files)), sorted(set(tests)), sorted(set(deps))

priority = json.loads(PRIORITY.read_text(encoding="utf-8"))
gate = json.loads(GATE.read_text(encoding="utf-8"))

tasks = []

for idx, item in enumerate(priority.get("queue", []), start=1):
    mission = item.get("mission", {})
    mission_text = json.dumps(mission, ensure_ascii=False)
    files, tests, deps = infer_targets(mission_text)

    tasks.append({
        "task_id": f"P4.84-T{idx:03d}",
        "source_priority_id": item.get("priority_id"),
        "priority_score": item.get("priority_score"),
        "priority_band": item.get("priority_band"),
        "approval_status": "PENDING_APPROVAL",
        "execution_status": "BLOCKED_BY_P4.83_GATE",
        "auto_execution_allowed": False,
        "mission": mission,
        "reconstruction": {
            "task_type": "IMPLEMENTATION_PLAN_ONLY",
            "target_files": files,
            "target_tests": tests,
            "dependencies": deps,
            "rollback_required": True,
            "evidence_required": True,
            "manual_approval_required": True
        }
    })

plan = {
    "milestone": "P4.84 COMPLETE",
    "engine": "CAPABILITY_RECONSTRUCTION_ENGINE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "source": str(PRIORITY),
    "governance_gate": str(GATE),
    "gate_status": {
        "automatic_implementation": gate.get("automatic_implementation"),
        "approval_required": gate.get("approval_required"),
        "default_state": gate.get("default_state")
    },
    "total_tasks": len(tasks),
    "execution_policy": {
        "implementation": "FORBIDDEN",
        "mode": "PLAN_ONLY",
        "approval_required": True,
        "next_required_gate": "MISSION_APPROVAL_CONTRACT"
    },
    "tasks": tasks
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

Path("runtime/implementation_plans/p484_task_backlog.json").write_text(
    json.dumps({
        "milestone": "P4.84 COMPLETE",
        "total_tasks": len(tasks),
        "tasks": tasks
    }, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps({
    "status": "P4.84 COMPLETE",
    "tasks": len(tasks),
    "mode": "PLAN_ONLY",
    "output": str(OUT),
    "next": "P4.85 DRIVE KNOWLEDGE GRAPH"
}, indent=2, ensure_ascii=False))
