"""ET665.R303: fail-closed content integrity gate, no runtime promotion.
Trusted digests must come from independently reviewed authority, not from CSV rows.
"""
import hashlib
from pathlib import Path

def verify_source_bytes(source, trusted_sha256, *, authority_verified=False):
    result={"integrity_verified":False,"causal_signal_verified":False,
            "correlation_certified":False,"runtime_promotion_allowed":False,
            "status":"QUARANTINE","issues":[]}
    if authority_verified is not True:
        result["issues"].append("TRUSTED_AUTHORITY_REQUIRED")
    if not isinstance(trusted_sha256,str) or len(trusted_sha256)!=64 or any(c not in "0123456789abcdef" for c in trusted_sha256.lower()):
        result["issues"].append("TRUSTED_SHA256_REQUIRED")
    if not isinstance(source,(str,Path)):
        result["issues"].append("SOURCE_INVALID")
        return result
    path=Path(source)
    if not path.is_file() or path.is_symlink():
        result["issues"].append("SOURCE_NOT_REGULAR_FILE")
        return result
    if result["issues"]:
        return result
    digest=hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda:handle.read(1024*1024),b""):
                digest.update(block)
    except OSError:
        result["issues"].append("SOURCE_UNREADABLE")
        return result
    if digest.hexdigest()!=trusted_sha256.lower():
        result["issues"].append("SHA256_MISMATCH")
        return result
    result["integrity_verified"]=True
    # Byte integrity alone does not prove provenance, replay causality, or trading alpha.
    return result
