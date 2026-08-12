import json
from pathlib import Path
from mind_trader.app.audits.institutional_audit_ledger import append_audit_event, verify_ledger, institutional_snapshot, export_audit_package, save_snapshot

def test_append_and_verify_ledger(tmp_path):
    p=tmp_path/"ledger.jsonl"
    append_audit_event("TEST_EVENT",{"ok":True},str(p))
    append_audit_event("SECOND_EVENT",{"ok":2},str(p))
    r=verify_ledger(str(p))
    assert r["valid"] is True
    assert r["events"]==2

def test_detects_tampering(tmp_path):
    p=tmp_path/"ledger.jsonl"
    append_audit_event("TEST_EVENT",{"ok":True},str(p))
    row=json.loads(p.read_text(encoding="utf-8").splitlines()[0])
    row["payload"]["ok"]=False
    p.write_text(json.dumps(row,ensure_ascii=False)+"\n",encoding="utf-8")
    r=verify_ledger(str(p))
    assert r["valid"] is False
    assert r["reason"]=="EVENT_HASH_MISMATCH"

def test_snapshot_contains_all_statuses():
    s=institutional_snapshot(96)
    assert s["tests_passed"]==96
    assert s["production"]=="BLOCKED"
    assert s["live"]=="FORBIDDEN"
    assert len(s["modules"])==17

def test_export_audit_package(tmp_path):
    ledger=tmp_path/"ledger.jsonl"
    append_audit_event("SNAPSHOT",{"tests":96},str(ledger))
    pkg=export_audit_package(str(tmp_path/"pkg.json"),str(ledger),96)
    assert pkg["ledger_integrity"]["valid"] is True
    assert pkg["snapshot"]["edge_claim"]=="NONE"

def test_save_snapshot(tmp_path):
    out=save_snapshot(str(tmp_path/"snap.json"),96)
    assert Path(out).exists()
