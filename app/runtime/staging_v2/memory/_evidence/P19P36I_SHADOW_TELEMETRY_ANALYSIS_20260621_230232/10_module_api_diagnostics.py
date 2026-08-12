import importlib, inspect, json
from pathlib import Path

mods = [
    "app.runtime.followup_unified_resolver",
    "app.runtime.generic_topic_memory_engine",
    "app.runtime.memory_adapter",
    "app.runtime.memory_store",
    "app.vision.vision_memory_store",
]

results = []

for m in mods:
    item = {"module": m, "import_ok": False, "members": [], "call_tests": []}
    try:
        mod = importlib.import_module(m)
        item["import_ok"] = True

        for name, obj in inspect.getmembers(mod):
            if name.startswith("_"):
                continue
            if inspect.isfunction(obj) or inspect.isclass(obj):
                sig = ""
                try:
                    sig = str(inspect.signature(obj))
                except Exception:
                    pass
                item["members"].append({
                    "name": name,
                    "type": "class" if inspect.isclass(obj) else "function",
                    "signature": sig
                })

        tests = [
            ("safe_recall", ("+TEST", "quero emagrecer")),
            ("safe_recall_with_fallback", ("+TEST", "quero emagrecer")),
            ("resolve_followup", ("+TEST", "quais")),
            ("expand_followup", ("quais", {"active_subject":"quero emagrecer"})),
            ("update_topic_context", ("+TEST", "quero emagrecer")),
            ("extract_subject", ("quero abrir escola de inglês",)),
            ("infer_domain", ("quero emagrecer",)),
            ("is_followup", ("quais",)),
        ]

        for fn_name, args in tests:
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    val = fn(*args)
                    item["call_tests"].append({
                        "function": fn_name,
                        "ok": True,
                        "result_preview": str(val)[:500]
                    })
                except Exception as e:
                    item["call_tests"].append({
                        "function": fn_name,
                        "ok": False,
                        "error": repr(e)
                    })

    except Exception as e:
        item["error"] = repr(e)

    results.append(item)

Path("_evidence/P19P36I_SHADOW_TELEMETRY_ANALYSIS_20260621_230232/module_api_diagnostics.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(results, ensure_ascii=False, indent=2))
