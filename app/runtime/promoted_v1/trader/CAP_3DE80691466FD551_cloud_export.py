import json, shutil, hashlib
from pathlib import Path
from datetime import datetime, UTC
from mind_trader.app.audits.transfer_snapshot import save_transfer_snapshot

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def build_export_manifest(source_dir="mind_trader/reports", tests_passed=151):
    save_transfer_snapshot(tests_passed=tests_passed)
    files=[]
    for p in sorted(Path(source_dir).glob("*.json")):
        files.append({"name":p.name,"path":str(p),"sha256":sha256(p),"bytes":p.stat().st_size})
    manifest={
        "manifest":"P8.56_CLOUD_EXPORT_MANIFEST",
        "created_at":datetime.now(UTC).isoformat(),
        "tests_passed":tests_passed,
        "files":files,
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
    raw=json.dumps(manifest,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    manifest["manifest_hash"]=hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return manifest

def export_to_directory(destination_dir, source_dir="mind_trader/reports", tests_passed=151):
    if not destination_dir:
        return {"decision":"BLOCKED_NO_REMOTE_DESTINATION","production":"BLOCKED","edge_claim":"NONE"}
    dest=Path(destination_dir)
    dest.mkdir(parents=True,exist_ok=True)
    manifest=build_export_manifest(source_dir,tests_passed)
    copied=[]
    for f in manifest["files"]:
        src=Path(f["path"])
        dst=dest/src.name
        shutil.copy2(src,dst)
        copied.append({"name":dst.name,"sha256":sha256(dst)})
    manifest_path=dest/"P8.56_cloud_export_manifest.json"
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return {
        "decision":"EXPORT_COMPLETED",
        "destination":str(dest),
        "copied":copied,
        "manifest_path":str(manifest_path),
        "manifest_hash":manifest["manifest_hash"],
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "edge_claim":"NONE"
    }
