"""ET665.R415: fail-closed E2E evidence verifier. Never executes untrusted code."""
import argparse
import hashlib
import json
from pathlib import Path

FORBIDDEN={"error","stub","noop","not_implemented","mock","synthetic"}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def verify(root, manifest, evidence):
    root=Path(root).resolve(strict=True)
    ids={x.get("historical_id") for x in manifest.get("hp19",[])}
    errors=[]
    if len(ids)!=19 or None in ids or len(manifest.get("hp19",[]))!=19:
        errors.append("INVALID_HP19_MANIFEST")
    runs=evidence.get("runs",[])
    if len(runs)!=19 or len({x.get("historical_id") for x in runs})!=19:
        errors.append("REQUIRES_19_UNIQUE_RUNS")
    observed=set()
    for run in runs:
        ident=run.get("historical_id")
        if ident not in ids:
            errors.append("UNKNOWN_MOTOR")
        if run.get("mode")!="PAPER" or run.get("real_orders") is not False:
            errors.append("UNSAFE_MODE")
        if run.get("status")!="PASS" or run.get("result_type") in FORBIDDEN:
            errors.append("INVALID_RESULT")
        for key in ("input","output","log"):
            value=run.get(key)
            expected=run.get(key+"_sha256")
            if not isinstance(value,str) or not isinstance(expected,str):
                errors.append("MISSING_ARTIFACT_OR_HASH")
                continue
            rel=Path(value)
            if rel.is_absolute() or ".." in rel.parts or rel.suffix not in (".json",".jsonl",".log",".txt"):
                errors.append("UNSAFE_ARTIFACT_PATH")
                continue
            target=root/rel
            if not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to(root):
                errors.append("ARTIFACT_MISSING_OR_SYMLINK")
                continue
            if sha(target)!=expected.lower():
                errors.append("ARTIFACT_HASH_MISMATCH")
            if key=="output":
                try:
                    obj=json.loads(target.read_text(encoding="utf-8"))
                    if not isinstance(obj,dict) or obj.get("status") in FORBIDDEN or obj.get("error") or obj.get("not_implemented"):
                        errors.append("OUTPUT_REJECTED")
                except (UnicodeError,ValueError):
                    errors.append("OUTPUT_NOT_JSON")
            if key in ("output","log"):
                marker=(key,str(target.resolve()))
                if marker in observed:
                    errors.append("REUSED_EVIDENCE")
                observed.add(marker)
        if not run.get("source_sha256") or not run.get("component_sha256"):
            errors.append("MISSING_SOURCE_OR_COMPONENT_PROVENANCE")
    return {"status":"READY_FOR_INDEPENDENT_REVIEW" if not errors else "BLOCKED",
            "self_certified":False,"verified_e2e":False,"errors":sorted(set(errors)),
            "runs":len(runs)}

def main():
    p=argparse.ArgumentParser()
    for name in ("root","manifest","evidence","output"):
        p.add_argument("--"+name,required=True)
    a=p.parse_args()
    result=verify(a.root,json.loads(Path(a.manifest).read_text()),json.loads(Path(a.evidence).read_text()))
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result))
    if result["status"]=="BLOCKED":
        raise SystemExit(2)
if __name__=="__main__":
    main()
