import json
import inspect
import importlib.util
import time
from pathlib import Path

ROOT=Path.cwd()
REGISTRY=ROOT/"app/runtime/shadow_registry/registry.json"

raw=json.loads(REGISTRY.read_text(encoding="utf-8"))
items=raw["capabilities"] if isinstance(raw,dict) else raw

profiles=[]

for item in items:

    path=item.get("path") or item.get("file") or item.get("module_path")
    full=ROOT/path

    p={
        "id":item.get("id"),
        "path":path,
        "exists":full.exists(),
        "entrypoints":[],
        "requires_input":[],
        "callable_count":0,
        "import_ok":False,
        "error":None
    }

    if not full.exists():
        profiles.append(p)
        continue

    try:

        spec=importlib.util.spec_from_file_location("tmpmod",full)
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        p["import_ok"]=True

        for n,o in inspect.getmembers(mod):

            if callable(o):

                p["callable_count"]+=1

                if n.startswith("_"):
                    continue

                try:
                    sig=str(inspect.signature(o))
                except:
                    sig="(?)"

                p["entrypoints"].append({
                    "name":n,
                    "signature":sig,
                    "async":inspect.iscoroutinefunction(o)
                })

                if sig!="()":
                    p["requires_input"].append(n)

    except Exception as e:
        p["error"]=str(e)

    profiles.append(p)

OUT=ROOT/"app/runtime/capability_profiles/capability_profiles.json"

OUT.write_text(
    json.dumps(profiles,indent=2,ensure_ascii=False),
    encoding="utf-8"
)

summary={
    "profiles":len(profiles),
    "import_ok":sum(x["import_ok"] for x in profiles),
    "missing":sum(not x["exists"] for x in profiles),
    "errors":sum(x["error"] is not None for x in profiles)
}

print(json.dumps(summary,indent=2,ensure_ascii=False))
