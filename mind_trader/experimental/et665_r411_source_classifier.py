"""ET665.R411: classify historical Python candidates without importing or executing them."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

def classify(root):
    root=Path(root).resolve()
    results=[]
    for path in sorted(root.rglob("*.py")):
        rel=path.relative_to(root).as_posix()
        if "agents_unified_runtime" not in rel and "/app/agents/" not in "/"+rel:
            continue
        record={"path":rel,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                "kind":"UNKNOWN","status":"UNCERTIFIED"}
        try:
            tree=ast.parse(path.read_bytes(),filename=rel)
            defs=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
            record["entrypoints"]=defs
            if path.name=="agents_unified_runtime.py":
                record["kind"]="DISPATCHER"
            elif "/app/agents/" in "/"+rel:
                record["kind"]="HISTORICAL_CANDIDATE" if "run_dry" in defs else "NON_EXECUTOR"
            imports=[]
            for node in tree.body:
                if isinstance(node,ast.ImportFrom):
                    imports.extend(alias.name for alias in node.names)
            if record["kind"]=="DISPATCHER" and imports.count("run_dry")>1:
                record["warning"]="DUPLICATE_RUN_DRY_IMPORT"
        except (SyntaxError,UnicodeError) as exc:
            record["kind"]="INVALID_SOURCE"
            record["warning"]=type(exc).__name__
        results.append(record)
    return {"status":"INVENTORY_ONLY","candidate_count":sum(x["kind"]=="HISTORICAL_CANDIDATE" for x in results),
            "functional_certified":0,"files":results}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    report=classify(args.root)
    Path(args.output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"candidate_count":report["candidate_count"],
                      "functional_certified":0,"files_scanned":len(report["files"])}))
if __name__=="__main__":
    main()
