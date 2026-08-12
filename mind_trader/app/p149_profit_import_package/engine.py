import json, shutil
from pathlib import Path
from datetime import datetime, UTC

SRC=Path("strategies/ntsl_massive_grid")
DEST=Path("profit_import_package")

def build_package(limit=50):
    DEST.mkdir(parents=True,exist_ok=True)
    items=[]
    folders=[p for p in SRC.iterdir() if p.is_dir()] if SRC.exists() else []
    for folder in folders[:limit]:
        code=folder/"code.nts"
        meta=folder/"metadata.json"
        if not code.exists():
            continue
        target=DEST/f"{folder.name}.nts"
        shutil.copy2(code,target)
        record={"strategy_id":folder.name,"file":str(target)}
        if meta.exists():
            record["metadata"]=json.loads(meta.read_text(encoding="utf-8"))
        items.append(record)
    return items

def run():
    out=Path("reports/P14.9_PROFIT_IMPORT_PACKAGE")
    out.mkdir(parents=True,exist_ok=True)
    items=build_package()
    manifest={
        "STATUS":"P14.9_PROFIT_IMPORT_PACKAGE_IMPLEMENTED",
        "FILES_PACKAGED":len(items),
        "PACKAGE_DIR":str(DEST),
        "IMPORT_TARGET":"Profit Editor de Estratégias / Importar Estratégia",
        "PAPER_ONLY":True,
        "LIVE":"FORBIDDEN",
        "REAL_BROKER":"DISABLED",
        "REAL_ORDERS":"FORBIDDEN",
        "EDGE":"NOT_PROVEN",
        "CAUSALITY":"NOT_PROVEN",
        "EXPORT_READY":True,
        "generated_at":datetime.now(UTC).isoformat()
    }
    (out/"profit_import_files.json").write_text(json.dumps(items,indent=2,ensure_ascii=False),encoding="utf-8")
    (out/"P14.9_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
