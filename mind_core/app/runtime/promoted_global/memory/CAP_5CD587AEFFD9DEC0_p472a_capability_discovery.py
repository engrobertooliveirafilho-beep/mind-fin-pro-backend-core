import json
import inspect
import traceback
import importlib
from pathlib import Path

MANIFEST = Path("app/runtime/memory_quarantine_manifest.json")

report = {
    "active_outside_pipeline": [],
    "summary": {},
}

if not MANIFEST.exists():
    print("MANIFEST_NOT_FOUND")
    raise SystemExit(1)

data = json.loads(MANIFEST.read_text(encoding="utf-8"))

targets = data.get("buckets", {}).get("ACTIVE_OUTSIDE_PIPELINE", [])

for module_name in targets:

    item = {
        "module": module_name,
        "import_ok": False,
        "functions": [],
        "classes": [],
        "error": None,
        "capability_score": 0,
    }

    try:

        mod = importlib.import_module(module_name)

        item["import_ok"] = True

        for name, obj in inspect.getmembers(mod):

            if inspect.isfunction(obj):
                item["functions"].append(name)

            elif inspect.isclass(obj):
                item["classes"].append(name)

        score = 0

        score += min(len(item["functions"]), 20)
        score += min(len(item["classes"]), 10)

        if "memory" in module_name.lower():
            score += 20

        if "retrieval" in module_name.lower():
            score += 20

        if "graph" in module_name.lower():
            score += 15

        if "social" in module_name.lower():
            score += 15

        if "dialogue" in module_name.lower():
            score += 15

        item["capability_score"] = score

    except Exception as e:

        item["error"] = (
            type(e).__name__
            + ": "
            + str(e)
        )

    report["active_outside_pipeline"].append(item)

report["active_outside_pipeline"] = sorted(
    report["active_outside_pipeline"],
    key=lambda x: x["capability_score"],
    reverse=True
)

report["summary"] = {
    "total_modules": len(report["active_outside_pipeline"]),
    "import_ok": len([
        x for x in report["active_outside_pipeline"]
        if x["import_ok"]
    ]),
    "import_failed": len([
        x for x in report["active_outside_pipeline"]
        if not x["import_ok"]
    ]),
}

Path("_evidence_report.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(report, indent=2, ensure_ascii=False))
print("P4.72A_DISCOVERY_COMPLETE")
