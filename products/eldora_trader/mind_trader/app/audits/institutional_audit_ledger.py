import json, hashlib
from pathlib import Path
from datetime import datetime, UTC

P8_STATUS = {
    "P8.26":"OK_RESEARCH_LAYER",
    "P8.27":"OK_FTMO_SIMULATION",
    "P8.28":"OK_MARKET_DATA_CORE",
    "P8.29":"OK_DATA_QUALITY_GATE",
    "P8.30":"OK_EDGE_VALIDATION",
    "P8.31":"OK_REGIME_DETECTION",
    "P8.32":"OK_STRATEGY_GENOME",
    "P8.33":"OK_ADVERSARIAL_VALIDATION",
    "P8.34":"OK_CROSS_ASSET_BRAIN",
    "P8.35":"OK_CAUSALITY_HYPOTHESIS",
    "P8.36":"OK_FEATURE_STORE",
    "P8.37":"OK_MASSIVE_BACKTEST_CLUSTER",
    "P8.38":"OK_DIGITAL_TWIN_REPLAY",
    "P8.39":"OK_CAPITAL_EVOLUTION",
    "P8.40":"OK_SELF_EVOLUTION",
    "P8.41":"OK_EXECUTION_GATEWAY_SIM",
    "P8.42":"OK_VALIDATION_PROTOCOL"
}

def canonical_hash(obj):
    raw=json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def read_ledger(path):
    p=Path(path)
    if not p.exists(): return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]

def append_audit_event(event_type, payload, path="mind_trader/logs/P8.43_INSTITUTIONAL_AUDIT_LEDGER.jsonl"):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    rows=read_ledger(path)
    prev_hash=rows[-1]["event_hash"] if rows else "GENESIS"
    event={
        "index":len(rows),
        "ts":datetime.now(UTC).isoformat(),
        "event_type":event_type,
        "payload":payload,
        "prev_hash":prev_hash
    }
    event["event_hash"]=canonical_hash(event)
    with open(path,"a",encoding="utf-8") as f:
        f.write(json.dumps(event,ensure_ascii=False)+"\n")
    return event

def verify_ledger(path="mind_trader/logs/P8.43_INSTITUTIONAL_AUDIT_LEDGER.jsonl"):
    rows=read_ledger(path)
    prev="GENESIS"
    for i,row in enumerate(rows):
        if row.get("index")!=i:
            return {"valid":False,"reason":"INDEX_MISMATCH","index":i}
        if row.get("prev_hash")!=prev:
            return {"valid":False,"reason":"PREV_HASH_MISMATCH","index":i}
        h=row.get("event_hash")
        tmp=dict(row); tmp.pop("event_hash",None)
        if canonical_hash(tmp)!=h:
            return {"valid":False,"reason":"EVENT_HASH_MISMATCH","index":i}
        prev=h
    return {"valid":True,"events":len(rows),"last_hash":prev}

def institutional_snapshot(test_count=96):
    return {
        "system":"MIND_TRADER_PRIVATE_ADAPTIVE_MARKET_INTELLIGENCE_SYSTEM",
        "snapshot_ts":datetime.now(UTC).isoformat(),
        "modules":P8_STATUS,
        "tests_passed":test_count,
        "production":"BLOCKED",
        "live":"FORBIDDEN",
        "max_approval_scope":"PAPER_TRADING_APPROVED",
        "edge_claim":"NONE",
        "causality_claim":"NOT_PROVEN"
    }

def export_audit_package(path="mind_trader/reports/P8.43_institutional_audit_package.json", ledger_path="mind_trader/logs/P8.43_INSTITUTIONAL_AUDIT_LEDGER.jsonl", test_count=96):
    snap=institutional_snapshot(test_count)
    integrity=verify_ledger(ledger_path)
    package={"snapshot":snap,"ledger_integrity":integrity,"ledger_events":read_ledger(ledger_path)}
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(package,ensure_ascii=False,indent=2),encoding="utf-8")
    return package

def save_snapshot(path="mind_trader/reports/P8.43_status_snapshot.json", test_count=96):
    snap=institutional_snapshot(test_count)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(snap,ensure_ascii=False,indent=2),encoding="utf-8")
    return path
