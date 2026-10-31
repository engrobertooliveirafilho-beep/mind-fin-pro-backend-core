"""R344 independent historical evidence gate: no hash baseline, no certification."""
import csv, hashlib, json
from pathlib import Path
from datetime import datetime

def verify_file(path, expected_sha256):
    if not isinstance(expected_sha256,str) or len(expected_sha256)!=64:
        return {"verified":False,"reason":"MISSING_INDEPENDENT_SHA256"}
    try:
        int(expected_sha256,16)
    except ValueError:
        return {"verified":False,"reason":"INVALID_SHA256"}
    p=Path(path)
    if not p.is_file():
        return {"verified":False,"reason":"MISSING_SOURCE_BYTES"}
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    actual=h.hexdigest()
    return {"verified":actual.lower()==expected_sha256.lower(),"reason":"MATCH" if actual.lower()==expected_sha256.lower() else "HASH_MISMATCH","actual_sha256":actual}

def verify_oos_chronology(train_end, test_start, test_end):
    try:
        values=[datetime.fromisoformat(str(x).replace("Z","+00:00")) for x in (train_end,test_start,test_end)]
        return values[0]<values[1]<=values[2]
    except (TypeError,ValueError):
        return False

def evidence_gate(source_path, independent_sha, train_end, test_start, test_end):
    source=verify_file(source_path,independent_sha)
    chronology=verify_oos_chronology(train_end,test_start,test_end)
    return {"source":source,"chronology_verified":chronology,"certified":False,
            "promotion_authorized":False,"status":"BLOCKED",
            "reason":"ORIGINAL_STRATEGY_AND_REPLAY_NOT_E2E_CERTIFIED"}
