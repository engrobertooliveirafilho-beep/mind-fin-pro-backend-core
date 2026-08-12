import json
from pathlib import Path
from app.p18_conversational_execution.internal_pilot import run_internal_pilot_dry_run

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P18H_INTERNAL_PILOT_OBSERVATION_20260616_230604")
obs_log = out / "P18H_OBSERVATION.jsonl"

iterations = 300
results = []

for i in range(iterations):
    result = run_internal_pilot_dry_run()
    record = {
        "iteration": i,
        "status": result["status"],
        "cases": result["cases"],
        "candidate_recommendations": result["candidate_recommendations"],
        "runtime_modified": result["runtime_modified"],
        "runtime_response_modified": result["runtime_response_modified"],
        "production_enabled": result["production_enabled"],
    }
    with obs_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    results.append(record)

pass_count = sum(1 for r in results if r["status"] == "PASS")
mutations = sum(1 for r in results if r["runtime_modified"] or r["runtime_response_modified"])
prod = sum(1 for r in results if r["production_enabled"])

report = {
    "mission": "P18H_INTERNAL_PILOT_OBSERVATION",
    "iterations": iterations,
    "pass_count": pass_count,
    "mutations": mutations,
    "production_enabled_count": prod,
    "runtime_modified": False,
    "runtime_response_modified": False,
    "production_enabled": False,
    "status": "PASS" if pass_count == iterations and mutations == 0 and prod == 0 else "FAIL",
    "next_required_action": "P18I_INTERNAL_PILOT_READINESS_CERTIFICATION"
}

(out / "P18H_INTERNAL_PILOT_OBSERVATION_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, ensure_ascii=False))
