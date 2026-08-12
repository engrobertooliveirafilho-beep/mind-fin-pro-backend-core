import time, json, importlib
from pathlib import Path
from datetime import datetime, timezone

targets = [
    "app.main",
    "app.eldora.core.agent_orchestrator",
    "app.eldora.core.task_engine",
    "app.eldora.core.distributed_runtime",
    "app.eldora.core.predictive_simulation_engine",
    "app.p7_adapters.hierarchical_planner_adapter",
]

rows = []
for t in targets:
    start = time.perf_counter()
    status = "PASS"
    error = None
    try:
        importlib.import_module(t)
    except Exception as e:
        status = "FAIL"
        error = str(e)
    elapsed = round(time.perf_counter() - start, 6)
    rows.append({
        "module": t,
        "status": status,
        "seconds": elapsed,
        "error": error
    })

out = Path("_evidence") / sorted([p.name for p in Path("_evidence").glob("P4.46_PERFORMANCE_PROFILING_*")])[-1] / "reports"
(out / "import_performance.json").write_text(json.dumps({
    "program": "P4.46_PERFORMANCE_PROFILING",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "imports": rows
}, indent=2), encoding="utf-8")

print(json.dumps(rows, indent=2))
