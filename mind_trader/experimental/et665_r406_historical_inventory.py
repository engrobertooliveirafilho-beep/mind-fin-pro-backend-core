"""ET665.R406: inspect recovered historical sources without executing them.
An inventory is not proof of functionality; unknown authority stays uncertified.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

DENIED={"stub","noop","not_implemented","error"}

def inspect(root, inventory):
    root=Path(root).resolve()
    result={"status":"FAIL_CLOSED","sources_found":0,"sources_sha256_verified":0,
            "functional_certified":0,"items":[]}
    try:
        items=json.loads(Path(inventory).read_text(encoding="utf-8"))["hp19"]
        if not isinstance(items,list) or len(items)!=19:
            raise ValueError("expected 19 historical sources")
        seen=set()
        for item in items:
            ident=item["historical_id"]
            rel=item["path"]
            expected=item["sha256"]
            if not isinstance(ident,str) or not ident or ident in seen:
                raise ValueError("invalid or duplicate historical id")
            seen.add(ident)
            if not isinstance(rel,str) or Path(rel).is_absolute():
                raise ValueError("unsafe source path")
            candidate=root/rel
            path=candidate.resolve()
            if not path.is_relative_to(root) or not path.is_file() or candidate.is_symlink():
                raise ValueError("missing or unsafe source")
            data=path.read_bytes()
            digest=hashlib.sha256(data).hexdigest()
            if digest!=expected:
                raise ValueError("source hash mismatch: "+ident)
            result["sources_found"]+=1
            result["sources_sha256_verified"]+=1
            tree=ast.parse(data,filename=str(path))
            funcs=[n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
            strings=[n.value.lower() for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
            warnings=sorted(x for x in DENIED if any(x in text for text in strings))
            result["items"].append({"historical_id":ident,"path":rel,"sha256":digest,
                                    "functions":funcs,"warning_tokens":warnings,
                                    "status":"SOURCE_VERIFIED_UNCERTIFIED"})
        result["status"]="SOURCES_VERIFIED_FUNCTIONAL_PENDING"
    except (OSError,ValueError,KeyError,TypeError,SyntaxError) as exc:
        result["error"]=type(exc).__name__+": "+str(exc)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--inventory",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=inspect(a.root,a.inventory)
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="SOURCES_VERIFIED_FUNCTIONAL_PENDING" else 1

if __name__=="__main__":
    raise SystemExit(main())
