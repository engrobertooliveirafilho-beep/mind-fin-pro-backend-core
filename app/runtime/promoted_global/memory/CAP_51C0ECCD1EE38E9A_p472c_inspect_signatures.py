import inspect
import importlib
import json

targets = [
    "app.eldora.core.persistent_social_memory",
    "app.eldora.core.long_term_memory",
    "app.api.eldora_social",
    "app.persona.adaptive_social_dialogue",
    "app.retrieval.provider",
]

out = {}

for module_name in targets:
    mod = importlib.import_module(module_name)
    out[module_name] = {}

    for name, obj in inspect.getmembers(mod):
        if name.startswith("_"):
            continue
        if inspect.isfunction(obj) or inspect.isclass(obj):
            try:
                out[module_name][name] = str(inspect.signature(obj))
            except Exception as e:
                out[module_name][name] = "SIGNATURE_ERROR:" + repr(e)

print(json.dumps(out, ensure_ascii=False, indent=2))
