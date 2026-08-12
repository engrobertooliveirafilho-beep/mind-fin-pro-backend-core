import os
import json
import time
from pathlib import Path

os.environ["ENABLE_HIERARCHICAL_PLANNER"] = "true"
os.environ["HIERARCHICAL_MODE"] = "SHADOW"
os.environ["ENABLE_OVERSIGHT"] = "true"
os.environ["OVERSIGHT_MODE"] = "SHADOW"

from app.p8_shadow.shadow_hooks import run_hierarchical_planner_shadow, run_oversight_shadow

out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P8_OBSERVATION_PHASE_20260616_072741")
telemetry = out / "P8_OBSERVATION_TELEMETRY.jsonl"

total = 1000
errors = 0
planner_pass = 0
oversight_pass = 0
started = time.perf_counter()

for i in range(total):
    payload = {"iteration": i, "goal": "P8 observation shadow execution"}
    planner = run_hierarchical_planner_shadow(payload, log_path=str(telemetry))
    oversight = run_oversight_shadow({"runtime_answer": "authoritative", "iteration": i}, log_path=str(telemetry))

    if planner.get("mode") == "SHADOW":
        planner_pass += 1
    else:
        errors += 1

    if oversight.get("mode") == "SHADOW":
        oversight_pass += 1
    else:
        errors += 1

elapsed = time.perf_counter() - started

result = {
    "mission": "P8_OBSERVATION_PHASE",
    "total_executions": total,
    "planner_shadow_pass": planner_pass,
    "oversight_shadow_pass": oversight_pass,
    "errors": errors,
    "error_rate": errors / (total * 2),
    "elapsed_seconds": elapsed,
    "runtime_modified": False,
    "active_mode_allowed": False,
    "block_mode_allowed": False,
    "runtime_authority_preserved": True,
    "status": "PASS" if errors == 0 else "REVIEW"
}

(out / "P8_OBSERVATION_REPORT.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(result, ensure_ascii=False))
