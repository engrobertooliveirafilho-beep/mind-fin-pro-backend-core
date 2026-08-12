import json
import importlib
import inspect
from pathlib import Path
from datetime import datetime, timezone

MODULES = [
    "app.runtime.cognitive_pipeline",
    "app.runtime.visible_response_layer",
    "app.runtime.response_generation_engine",
    "app.runtime.whatsapp_final_output_guard",
    "app.api.whatsapp",
    "app.eldora.core.audit_ledger",
    "app.eldora.core.event_bus",
    "app.runtime.knowledge_extraction_engine",
    "app.runtime.p479_knowledge_extraction_engine",
]

out = {
    "mission": "P4.82C ACTIVE_RUNTIME_IMPORT_TRACE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "modules": []
}

for m in MODULES:
    row = {"module": m, "imported": False}
    try:
        mod = importlib.import_module(m)
        row["imported"] = True
        row["file"] = getattr(mod, "__file__", None)
        row["functions"] = []
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if name in [
                "run_cognitive_pipeline",
                "eldora_primary_runtime_reply",
                "audit_event",
                "audit_report",
                "publish",
                "event_bus_report",
                "extract_items",
            ]:
                row["functions"].append({
                    "name": name,
                    "source_file": inspect.getsourcefile(obj),
                    "line": getattr(obj, "__code__", None).co_firstlineno if getattr(obj, "__code__", None) else None
                })
    except Exception as e:
        row["error"] = repr(e)
    out["modules"].append(row)

Path("runtime/import_trace/active_runtime_import_trace.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print(json.dumps(out, indent=2, ensure_ascii=False))
