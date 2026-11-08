"""ET665.R122: offline single-session reconciliation contract."""
import importlib.util
import json
import sqlite3
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "security/et665_r122_paper_reconciliation.py"
spec = importlib.util.spec_from_file_location("et665_r122", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixtures(tmp_path, state="FILLED", trades=1, accepted=True):
    db, session, broker = (tmp_path / x for x in ("capacity.sqlite", "session.json", "broker.jsonl"))
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE reservations(session_id TEXT, order_id TEXT, state TEXT)")
        conn.execute("INSERT INTO reservations VALUES ('s1','o1',?)", (state,))
    session.write_text(json.dumps({"session_id": "s1", "trades": trades, "status": "OPEN"}))
    event = {"decision": "PAPER_ORDER_ACCEPTED" if accepted else "PAPER_ORDER_REJECTED",
             "order": {"session_id": "s1", "capacity_order_id": "o1"},
             "fill": {"filled": accepted}}
    broker.write_text(json.dumps(event) + "\n")
    return db, session, broker


def test_matching_filled_reservation_and_session(tmp_path):
    result = mod.audit_paper_consistency(*fixtures(tmp_path))
    assert result["certified"] is True
    assert result["production"] == "BLOCKED"


def test_uncertain_reservation_blocks(tmp_path):
    result = mod.audit_paper_consistency(*fixtures(tmp_path, state="RESERVED", trades=0))
    assert result["certified"] is False
    assert "BLOCK_UNCERTAIN_RESERVATION" in result["findings"]


def test_missing_session_accounting_blocks(tmp_path):
    result = mod.audit_paper_consistency(*fixtures(tmp_path, trades=0))
    assert "BLOCK_SESSION_TRADE_COUNT_MISMATCH" in result["findings"]


def test_broker_acceptance_without_finalization_blocks(tmp_path):
    result = mod.audit_paper_consistency(*fixtures(tmp_path, state="REJECTED", trades=0))
    assert "BLOCK_ACCEPTED_NOT_FINALIZED" in result["findings"]


def test_missing_broker_ledger_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    broker.unlink()
    result = mod.audit_paper_consistency(db, session, broker)
    assert result["certified"] is False


def test_rejected_reservation_no_fill_can_reconcile(tmp_path):
    result = mod.audit_paper_consistency(*fixtures(tmp_path, state="REJECTED", trades=0, accepted=False))
    assert result["certified"] is True


def test_orphan_broker_event_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    event = json.loads(broker.read_text())
    event["order"]["capacity_order_id"] = "missing"
    broker.write_text(json.dumps(event) + "\n")
    result = mod.audit_paper_consistency(db, session, broker)
    assert "BLOCK_ORPHAN_BROKER_EVENT" in result["findings"]


def test_empty_evidence_cannot_be_certified(tmp_path):
    db, session, broker = fixtures(tmp_path, state="REJECTED", trades=0, accepted=False)
    with sqlite3.connect(db) as conn:
        conn.execute("DELETE FROM reservations")
    broker.write_text("")
    result = mod.audit_paper_consistency(db, session, broker)
    assert result["certified"] is False
    assert "BLOCK_NO_ORDER_LEVEL_EVIDENCE" in result["findings"]


def test_invalid_session_status_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    payload = json.loads(session.read_text())
    payload["status"] = "UNKNOWN"
    session.write_text(json.dumps(payload))
    result = mod.audit_paper_consistency(db, session, broker)
    assert "BLOCK_INVALID_SESSION_STATUS" in result["findings"]


def test_duplicate_broker_event_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    broker.write_text(broker.read_text() * 2)
    result = mod.audit_paper_consistency(db, session, broker)
    assert "BLOCK_DUPLICATE_BROKER_EVENT" in result["findings"]


def test_persisted_broker_claims_live_routing_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    receipt = json.loads(broker.read_text())
    receipt["real_broker_routing"] = "ENABLED"
    broker.write_text(json.dumps(receipt) + "\n")
    result = mod.audit_paper_consistency(db, session, broker)
    assert result["certified"] is False
    assert "BLOCK_PERSISTED_BROKER_LIVE_ROUTING_CLAIM" in result["findings"]


def test_persisted_broker_claims_external_identity_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    receipt = json.loads(broker.read_text())
    receipt["broker"] = "MT5_REAL"
    broker.write_text(json.dumps(receipt) + "\n")
    result = mod.audit_paper_consistency(db, session, broker)
    assert result["certified"] is False
    assert "BLOCK_PERSISTED_BROKER_LIVE_ROUTING_CLAIM" in result["findings"]


def test_persisted_broker_order_claims_live_mode_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    receipt = json.loads(broker.read_text())
    receipt["order"]["mode"] = "FTMO_REAL"
    broker.write_text(json.dumps(receipt) + "\n")
    result = mod.audit_paper_consistency(db, session, broker)
    assert result["certified"] is False
    assert "BLOCK_PERSISTED_BROKER_ORDER_LIVE_CLAIM" in result["findings"]


def test_persisted_broker_order_claims_real_routing_blocks(tmp_path):
    db, session, broker = fixtures(tmp_path)
    receipt = json.loads(broker.read_text())
    receipt["order"]["real_broker_routing"] = "ENABLED"
    broker.write_text(json.dumps(receipt) + "\n")
    result = mod.audit_paper_consistency(db, session, broker)
    assert result["certified"] is False
    assert "BLOCK_PERSISTED_BROKER_ORDER_LIVE_CLAIM" in result["findings"]
