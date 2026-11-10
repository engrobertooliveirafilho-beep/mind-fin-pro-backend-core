"""ET665.R413: independent HP19 manifest reconciliation; no code execution."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

HASH=re.compile(r"^[a-fA-F0-9]{64}$")

def reconcile(root, inventory, manifest):
    root=Path(root).resolve(strict=True)
    records=inventory.get("files",[])
    declared=manifest.get("hp19",[])
    errors=[]
    if len(declared)!=19:
        errors.append("MANIFEST_MUST_HAVE_EXACTLY_19")
    if len(records)==0:
        errors.append("INVENTORY_EMPTY")
    paths=set()
    ids=set()
    inventory_by_path={x.get("path"):x for x in records}
    for item in declared:
        ident=item.get("historical_id")
        raw=item.get("path")
        expected=item.get("sha256")
        if not isinstance(ident,str) or not ident.strip() or ident in ids:
            errors.append("INVALID_OR_DUPLICATE_ID")
        ids.add(ident)
        if not isinstance(raw,str) or not raw or "\\" in raw:
            errors.append("INVALID_PATH")
            continue
        p=PurePosixPath(raw)
        if p.is_absolute() or ".." in p.parts or p.suffix!=".py" or raw in paths:
            errors.append("UNSAFE_OR_DUPLICATE_PATH")
            continue
        paths.add(raw)
        if not isinstance(expected,str) or not HASH.fullmatch(expected):
            errors.append("INVALID_EXPECTED_HASH")
            continue
        target=root.joinpath(*p.parts)
        if any(x.is_symlink() for x in (target,*target.parents) if x!=root and root in x.parents):
            errors.append("SYMLINK_FORBIDDEN")
            continue
        if not target.is_file() or not target.resolve().is_relative_to(root):
            errors.append("SOURCE_MISSING_OR_OUTSIDE")
            continue
        actual=hashlib.sha256(target.read_bytes()).hexdigest()
        if actual!=expected.lower():
            errors.append("SOURCE_HASH_MISMATCH")
        indexed=inventory_by_path.get(raw)
        if not indexed or indexed.get("kind")!="HISTORICAL_CANDIDATE":
            errors.append("NOT_A_CLASSIFIED_EXECUTOR")
        elif indexed.get("sha256","").lower()!=actual:
            errors.append("INVENTORY_HASH_MISMATCH")
    return {"status":"IDENTITY_VERIFIED" if not errors else "BLOCKED",
            "identity_verified":len(errors)==0,"functional_certified":0,
            "manifest_count":len(declared),"errors":sorted(set(errors))}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True)
    parser.add_argument("--inventory",required=True)
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    result=reconcile(args.root,json.loads(Path(args.inventory).read_text()),
                     json.loads(Path(args.manifest).read_text()))
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result))
    if not result["identity_verified"]:
        raise SystemExit(2)

if __name__=="__main__":
    main()
