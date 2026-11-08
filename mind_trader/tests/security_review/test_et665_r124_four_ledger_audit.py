"""ET665.R124 four-ledger fail-closed regressions."""
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

SECURITY = Path(__file__).resolve().parents[2] / "security"
sys.path.insert(0, str(SECURITY))
from et665_r124_four_ledger_audit import audit_four_ledgers


def fixtures(tmp_path):
    db, session, broker, execution = [tmp_path / name for name in
                                      ("capacity.sqlite", "session.json", "broker.jsonl", "execution.jsonl")]
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE reservations(session_id TEXT, order_id TEXT, state TEXT)")
        conn.execute("INSERT INTO reservations VALUES ('s1','o1','FILLED')")
    session.write_text(json.dumps({"session_id":"s1","status":"OPEN","trades":1}))
    b = {"decision":"PAPER_ORDER_ACCEPTED","order":{"session_id":"s1","capacity_order_id":"o1"},
         "fill":{"filled":True}}
    broker.write_text(json.dumps(b)+"\n")
    e = {"mode":"PAPER","decision":"ACCEPT_SIMULATED_ORDER","capacity_decision":"FILLED",
         "capacity_order_id":"o1","paper_broker":b}
    execution.write_text(json.dumps(e)+"\n")
    return db,session,broker,execution


def test_four_ledgers_matching(tmp_path):
    assert audit_four_ledgers(*fixtures(tmp_path))["certified"] is True


def test_execution_ledger_missing_blocks(tmp_path):
    paths = fixtures(tmp_path)
    paths[-1].unlink()
    assert "BLOCK_EXECUTION_LEDGER_UNAVAILABLE" in audit_four_ledgers(*paths)["findings"]


def test_accepted_without_confirmed_fill_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["paper_broker"]["fill"]["filled"] = False
    paths[-1].write_text(json.dumps(event)+"\n")
    assert "BLOCK_EXECUTION_ACCEPTANCE_CONTRADICTION" in audit_four_ledgers(*paths)["findings"]


def test_duplicate_execution_order_blocks(tmp_path):
    paths = fixtures(tmp_path)
    paths[-1].write_text(paths[-1].read_text()*2)
    assert "BLOCK_DUPLICATE_EXECUTION_ORDER" in audit_four_ledgers(*paths)["findings"]


def test_rejected_filled_order_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["decision"] = "REJECT_ORDER"
    paths[-1].write_text(json.dumps(event)+"\n")
    assert "BLOCK_FILLED_EXECUTION_REJECTED" in audit_four_ledgers(*paths)["findings"]


def test_other_execution_cannot_mask_missing_filled_order(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["capacity_order_id"] = "different-order"
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert "BLOCK_MISSING_EXECUTION_CORRELATION" in result["findings"]


def test_rejected_execution_cannot_mask_filled_reservation(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["decision"] = "REJECT_ORDER"
    event["capacity_decision"] = "BLOCK_CAPACITY_ERROR"
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert "BLOCK_MISSING_EXECUTION_CORRELATION" in result["findings"]
