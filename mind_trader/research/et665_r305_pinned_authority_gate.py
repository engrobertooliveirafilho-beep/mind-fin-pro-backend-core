"""ET665.R305: pinned-manifest authority gate for offline research inputs.
Trust anchor is a SHA256 supplied by independent reviewer, not by a CSV row.
This is integrity/authority preflight only, never causal certification.
"""
import hashlib
import json
import re
from pathlib import Path

_HEX = re.compile(r"^[0-9a-fA-F]{64}$")

def verify_pinned_manifest(source, manifest, trusted_manifest_sha256, *, source_id):
    out = {"authority_integrity_verified":False,"source_integrity_verified":False,
           "causal_signal_verified":False,"runtime_promotion_allowed":False,
           "status":"QUARANTINE","issues":[]}
    if not isinstance(trusted_manifest_sha256,str) or not _HEX.fullmatch(trusted_manifest_sha256):
        out["issues"].append("TRUST_ANCHOR_REQUIRED")
        return out
    if not isinstance(source_id,str) or not source_id.strip():
        out["issues"].append("SOURCE_ID_REQUIRED")
        return out
    if not isinstance(source,(str,Path)) or not isinstance(manifest,(str,Path)):
        out["issues"].append("INVALID_PATH")
        return out
    try:
        mpath=Path(manifest)
        spath=Path(source)
        if mpath.is_symlink() or not mpath.is_file() or spath.is_symlink() or not spath.is_file():
            out["issues"].append("FILE_UNAVAILABLE_OR_SYMLINK")
            return out
        manifest_bytes=mpath.read_bytes()
        if hashlib.sha256(manifest_bytes).hexdigest()!=trusted_manifest_sha256.lower():
            out["issues"].append("MANIFEST_HASH_MISMATCH")
            return out
        out["authority_integrity_verified"]=True
        doc=json.loads(manifest_bytes)
        if not isinstance(doc,dict) or doc.get("schema")!="ET665_TRUSTED_SOURCE_MANIFEST_V1":
            out["issues"].append("MANIFEST_SCHEMA_INVALID")
            return out
        entries=doc.get("sources")
        if not isinstance(entries,dict) or source_id not in entries:
            out["issues"].append("SOURCE_NOT_IN_MANIFEST")
            return out
        item=entries[source_id]
        if not isinstance(item,dict) or item.get("source_kind")!="CAUSAL_STRATEGY_REPLAY":
            out["issues"].append("SOURCE_KIND_UNVERIFIED")
            return out
        expected=item.get("sha256")
        if not isinstance(expected,str) or not _HEX.fullmatch(expected):
            out["issues"].append("SOURCE_HASH_INVALID")
            return out
        digest=hashlib.sha256()
        with spath.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""):
                digest.update(chunk)
        if digest.hexdigest()!=expected.lower():
            out["issues"].append("SOURCE_HASH_MISMATCH")
            return out
        out["source_integrity_verified"]=True
    except (OSError,ValueError,TypeError,UnicodeError):
        out["issues"].append("MANIFEST_OR_SOURCE_UNREADABLE")
    return out
