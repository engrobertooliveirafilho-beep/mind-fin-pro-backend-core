"""R388 strict causal walk-forward replay; PAPER ONLY; no data generation."""
import csv
from datetime import datetime, timezone
from pathlib import Path

def replay(path, *, expected_sha256, train_end, test_start, test_end):
    from sys import path as sys_path
    sys_path.insert(0, str(Path(__file__).resolve().parents[1] / "r344_evidence"))
    from provenance_gate import verify_file, verify_oos_chronology
    provenance=verify_file(path,expected_sha256)
    if not provenance["verified"] or not verify_oos_chronology(train_end,test_start,test_end):
        return {"status":"BLOCKED","reason":"PROVENANCE_OR_CHRONOLOGY","promotion_authorized":False}
    rows=[]
    with open(path,newline="",encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            ts=datetime.fromisoformat(row["time"].replace("Z","+00:00"))
            if ts.tzinfo is None: ts=ts.replace(tzinfo=timezone.utc)
            rows.append((ts,float(row["close"])))
    if len(rows)<3 or any(rows[i][0]>=rows[i+1][0] for i in range(len(rows)-1)):
        return {"status":"BLOCKED","reason":"NON_MONOTONIC_OR_SHORT","promotion_authorized":False}
    a=datetime.fromisoformat(train_end.replace("Z","+00:00"))
    b=datetime.fromisoformat(test_start.replace("Z","+00:00"))
    c=datetime.fromisoformat(test_end.replace("Z","+00:00"))
    if any(x.tzinfo is None for x in (a,b,c)):
        return {"status":"BLOCKED","reason":"TIMEZONE_REQUIRED","promotion_authorized":False}
    if not any(t<=a for t,_ in rows) or not any(b<=t<=c for t,_ in rows):
        return {"status":"BLOCKED","reason":"MISSING_TRAIN_OR_TEST","promotion_authorized":False}
    scores=[]
    for i in range(1,len(rows)-1):
        t,close=rows[i]
        if not b<=t<=c: continue
        if rows[i+1][0]>c: continue
        previous=rows[i-1][1]
        direction=1 if close>previous else -1 if close<previous else 0
        if direction: scores.append(direction*(rows[i+1][1]-close)/close)
    return {"status":"PAPER_REPLAY_ONLY","signals":len(scores),"mean_forward_return":sum(scores)/len(scores) if scores else None,"promotion_authorized":False,"ftmo_certified":False}
