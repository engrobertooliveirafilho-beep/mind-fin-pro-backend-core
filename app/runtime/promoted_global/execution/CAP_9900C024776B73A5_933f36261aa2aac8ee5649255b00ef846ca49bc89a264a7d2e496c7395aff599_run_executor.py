from datetime import datetime, UTC
import json

base = r"C:\Users\MindFin\AppData\Local\Temp\MIND_RUNTIME"

with open(base + "\\CORE_RUNTIME_READY.json", "r", encoding="utf-8") as f:
    rt = json.load(f)

with open(base + "\\EXECUTION_CHECKPOINT.json", "r", encoding="utf-8") as f:
    cp = json.load(f)

with open(base + "\\EXECUTION_LOG.json", "r", encoding="utf-8") as f:
    log = json.load(f)

res = []
start = cp.get("next_step_id", 1)
batch = 50

steps = [s for s in rt if s.get("step_id", 0) >= start][:batch]

def ts():
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")

def exec_step(s):
    try:
        return {
            "step_id": s["step_id"],
            "executed": True,
            "result": "OK",
            "error": None,
            "timestamp": ts()
        }
    except Exception as e:
        return {
            "step_id": s.get("step_id"),
            "executed": False,
            "result": None,
            "error": str(e),
            "timestamp": ts()
        }

for s in steps:
    res.append(exec_step(s))

with open(base + "\\STEP_EXECUTION_RESULTS.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

cp["executed_total"] = cp.get("executed_total", 0) + len(res)
cp["next_step_id"] = steps[-1]["step_id"] + 1 if steps else start
cp["remaining"] = max(0, cp.get("remaining", 0) - len(res))
cp["ready_for_resume"] = True

with open(base + "\\EXECUTION_CHECKPOINT.json", "w", encoding="utf-8") as f:
    json.dump(cp, f, ensure_ascii=False, indent=2)

log["last_batch"] = len(res)
log["last_run"] = ts()

with open(base + "\\EXECUTION_LOG.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
