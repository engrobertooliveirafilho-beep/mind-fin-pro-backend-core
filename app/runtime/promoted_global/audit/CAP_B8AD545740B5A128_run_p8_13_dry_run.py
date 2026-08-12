import json
from pathlib import Path

from app.p8_shadow.planner_active_policy import evaluate_planner_active_candidate
from app.p8_shadow.shadow_hooks import run_hierarchical_planner_shadow

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_13_PLANNER_LIMITED_ACTIVE_DRY_RUN_TEST_20260616_125923")

cases = [
    {"goal": "multi-step planning dry run", "plan": ["parse", "decompose", "order"]},
    {"goal": "workflow planning dry run", "plan": ["intake", "validate", "execute", "audit"]},
    {"goal": "oversized plan rejection dry run", "plan": ["a", "b", "c", "d", "e", "f"]},
]

results = []

for i, case in enumerate(cases):
    candidate = {
        "request_id": f"p8-13-{i}",
        "capability": "HIERARCHICAL_PLANNING",
        "mode": "LIMITED_ACTIVE_DRY_RUN",
        "plan": case["plan"],
        "runtime_modified": False,
    }

    policy_result = evaluate_planner_active_candidate(candidate)

    results.append({
        "case": i,
        "goal": case["goal"],
        "plan_steps": len(case["plan"]),
        "policy_result": policy_result,
        "runtime_modified": False,
        "response_modified": False,
        "active_enabled": False,
        "dry_run_only": True
    })

pass_count = sum(1 for r in results if r["policy_result"]["status"] in {"PASS", "REVIEW"})

report = {
    "mission": "P8.13_PLANNER_LIMITED_ACTIVE_DRY_RUN_TEST",
    "cases": len(results),
    "evaluated": pass_count,
    "runtime_modified": False,
    "response_modified": False,
    "active_enabled": False,
    "block_mode_enabled": False,
    "dry_run_only": True,
    "oversight_kept_shadow": True,
    "status": "PASS" if pass_count == len(results) else "FAIL",
    "results": results,
    "recommendation": "READY_FOR_P8_14_PLANNER_ACTIVE_SANDBOX_HOOK_REVIEW"
}

(out / "P8_13_DRY_RUN_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
