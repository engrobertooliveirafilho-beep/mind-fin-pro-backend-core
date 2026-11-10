"""ET665.R315: immutable source snapshot guard for offline P2404.
Use one byte snapshot for hashing and parsing, preventing source swap after verification.
Never certifies causality or enables trading.
"""
import hashlib
import io
import csv
import os
import stat
from pathlib import Path

def snapshot_verified_csv(source, expected_sha256, *, max_bytes=16_000_000):
    result={"verified":False,"issues":[],"rows":[],"runtime_promotion_allowed":False}
    try:
        p=Path(source)
        if p.is_symlink() or not p.is_file():
            result["issues"]=["INVALID_SOURCE_PATH"]
            return result
        if not isinstance(expected_sha256,str) or len(expected_sha256)!=64 or any(c not in "0123456789abcdefABCDEF" for c in expected_sha256):
            result["issues"]=["EXPECTED_HASH_REQUIRED"]
            return result
        if type(max_bytes) is not int or max_bytes < 1 or max_bytes > 16_000_000:
            result["issues"]=["INVALID_SIZE_LIMIT"]
            return result
        # Fail closed on platforms without atomic no-follow support (including Windows).
        # Do not silently fall back to a race-prone path check.
        if not hasattr(os, "O_NOFOLLOW"):
            result["issues"]=["ATOMIC_NOFOLLOW_UNAVAILABLE"]
            return result
        # Reject a symlink substituted after path validation; read only the opened inode.
        flags = os.O_RDONLY | os.O_NOFOLLOW
        fd = os.open(p, flags)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                result["issues"]=["INVALID_SOURCE_PATH"]
                return result
            payload=handle.read(max_bytes+1)
        if len(payload)>max_bytes:
            result["issues"]=["SOURCE_TOO_LARGE"]
            return result
        if hashlib.sha256(payload).hexdigest()!=expected_sha256.lower():
            result["issues"]=["SOURCE_HASH_MISMATCH"]
            return result
        stream=io.StringIO(payload.decode("utf-8-sig"),newline="")
        reader=csv.DictReader(stream,strict=True)
        if reader.fieldnames!=["edge_id","timestamp","pnl_r"]:
            result["issues"]=["INVALID_CSV_SCHEMA"]
            return result
        rows=[]
        for row in reader:
            if len(rows)>=100_000 or None in row or None in row.values():
                result["issues"]=["INVALID_CSV_ROWS"]
                return result
            rows.append(row)
        result["verified"]=True
        result["rows"]=rows
    except (OSError,UnicodeError,csv.Error,ValueError,TypeError):
        result["issues"]=["SOURCE_UNREADABLE"]
    return result
