import json, hashlib
from pathlib import Path

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def verify_export_directory(destination_dir):
    dest=Path(destination_dir)
    manifest_path=dest/"P8.56_cloud_export_manifest.json"
    if not manifest_path.exists():
        return {"decision":"EXPORT_VERIFY_FAILED","reason":"MANIFEST_NOT_FOUND","production":"BLOCKED","edge_claim":"NONE"}
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    failures=[]
    for item in manifest.get("files",[]):
        p=dest/item["name"]
        if not p.exists():
            failures.append({"file":item["name"],"reason":"MISSING"})
        elif sha256(p)!=item["sha256"]:
            failures.append({"file":item["name"],"reason":"HASH_MISMATCH"})
    return {
        "decision":"EXPORT_VERIFY_OK" if not failures else "EXPORT_VERIFY_FAILED",
        "failures":failures,
        "verified_files":len(manifest.get("files",[]))-len(failures),
        "manifest_hash":manifest.get("manifest_hash"),
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
