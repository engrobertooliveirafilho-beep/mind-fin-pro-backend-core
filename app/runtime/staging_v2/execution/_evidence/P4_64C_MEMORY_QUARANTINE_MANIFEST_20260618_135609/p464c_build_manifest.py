import json
from pathlib import Path

report_path = Path("C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core\\_evidence\\P4_64B_REAL_MEMORY_DEPENDENCY_GRAPH_20260618_135127\\dependency_graph_report.txt")
text = report_path.read_text(encoding="utf-8", errors="ignore")

json_text = text.split("\n" + "=" * 90)[0]
data = json.loads(json_text)

classification = data["classification"]

buckets = {
    "ACTIVE_IN_PIPELINE": [],
    "ACTIVE_IN_WHATSAPP_ADAPTER": [],
    "ACTIVE_OUTSIDE_PIPELINE": [],
    "ORPHANED_OR_UNUSED": [],
}

for mod, info in classification.items():
    buckets[info["classification"]].append(mod)

manifest = {
    "mission": "P4.64C_MEMORY_QUARANTINE_MANIFEST",
    "policy": {
        "delete_files": False,
        "quarantine_type": "logical_manifest_only",
        "active_modules_may_be_used": [
            "ACTIVE_IN_PIPELINE",
            "ACTIVE_IN_WHATSAPP_ADAPTER",
            "ACTIVE_OUTSIDE_PIPELINE"
        ],
        "orphaned_modules_policy": "do_not_integrate_without_explicit_revalidation"
    },
    "buckets": {k: sorted(v) for k, v in buckets.items()},
    "counts": {k: len(v) for k, v in buckets.items()},
}

Path("app/runtime").mkdir(parents=True, exist_ok=True)
out = Path("app/runtime/memory_quarantine_manifest.json")
out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(manifest, ensure_ascii=False, indent=2))
print("MANIFEST_WRITTEN:", out)
