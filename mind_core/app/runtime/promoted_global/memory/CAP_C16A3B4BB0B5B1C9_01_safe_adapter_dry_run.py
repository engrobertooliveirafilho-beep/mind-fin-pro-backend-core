import csv, importlib, json, inspect
from pathlib import Path
from datetime import datetime, timezone

EVID = Path("_evidence\\P19P36G_SAFE_ADAPTER_INTEGRATION_DRY_RUN_20260621_225229")
rows = list(csv.DictReader(open(EVID / "integrate_now.csv", encoding="utf-8")))

out = []

for r in rows:
    file_path = r["Module"].replace("\\", "/")
    mod_name = file_path.replace("/", ".").replace(".py", "")

    item = {
        "module": r["Module"],
        "module_name": mod_name,
        "import_ok": False,
        "functions": [],
        "classes": [],
        "safe_adapter_candidate": False,
        "reason": "",
    }

    try:
        mod = importlib.import_module(mod_name)
        item["import_ok"] = True

        for name, obj in inspect.getmembers(mod):
            if inspect.isfunction(obj) and not name.startswith("_"):
                item["functions"].append(name)
            if inspect.isclass(obj) and not name.startswith("_"):
                item["classes"].append(name)

        joined = " ".join(item["functions"] + item["classes"]).lower()
        if any(k in joined for k in ["memory", "store", "get", "save", "resolve", "followup", "context", "recall", "profile"]):
            item["safe_adapter_candidate"] = True
            item["reason"] = "Importa e expõe função/classe compatível com memória, contexto ou followup."
        else:
            item["reason"] = "Importa, mas não expõe API óbvia para adapter seguro."

    except Exception as e:
        item["reason"] = repr(e)

    out.append(item)

(EVID / "safe_adapter_dry_run.json").write_text(json.dumps({
    "mission": "P19P36G_SAFE_ADAPTER_INTEGRATION_DRY_RUN",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "results": out
}, ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps(out, ensure_ascii=False, indent=2))
