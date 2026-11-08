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


def test_execution_session_mismatch_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["session_id"] = "another-session"
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_EXECUTION_SESSION_MISMATCH" in result["findings"]


def test_accepted_execution_without_filled_reservation_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["capacity_order_id"] = "orphan-accepted"
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_EXECUTION_ACCEPTED_WITHOUT_FILLED_RESERVATION" in result["findings"]


def test_offline_consistency_never_certifies_operational_gateway(tmp_path):
    result = audit_four_ledgers(*fixtures(tmp_path))
    assert result["certified"] is True
    assert result["operational_certified"] is False
    assert result["production"] == "BLOCKED"


def test_missing_execution_ledger_never_certifies_operational_gateway(tmp_path):
    paths = fixtures(tmp_path)
    paths[-1].unlink()
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert result["operational_certified"] is False


def test_non_object_session_fails_closed_without_exception(tmp_path):
    paths = fixtures(tmp_path)
    paths[1].write_text("[]")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert result["operational_certified"] is False
    assert "BLOCK_EXECUTION_LEDGER_UNAVAILABLE" in result["findings"]


def test_non_object_execution_event_fails_closed(tmp_path):
    paths = fixtures(tmp_path)
    paths[-1].write_text("[]\n")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert "BLOCK_EXECUTION_LEDGER_UNAVAILABLE" in result["findings"]


def test_live_routing_claim_blocks_offline_certification(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["real_broker_routing"] = "ENABLED"
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_EXECUTION_LIVE_ROUTING_CLAIM" in result["findings"]


def test_accepted_execution_missing_order_id_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event.pop("capacity_order_id")
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_ACCEPTED_EXECUTION_UNCORRELATED" in result["findings"]


def test_embedded_broker_order_mismatch_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["paper_broker"]["order"]["capacity_order_id"] = "other"
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_EMBEDDED_BROKER_ORDER_MISMATCH" in result["findings"]


def test_embedded_broker_session_mismatch_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["paper_broker"]["order"]["session_id"] = "other"
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_EMBEDDED_BROKER_ORDER_MISMATCH" in result["findings"]


def test_embedded_receipt_differs_from_persisted_broker_event(tmp_path):
    paths = fixtures(tmp_path)
    event = json.loads(paths[-1].read_text())
    event["paper_broker"]["fill"]["price"] = 123.45
    paths[-1].write_text(json.dumps(event)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_EMBEDDED_BROKER_LEDGER_MISMATCH" in result["findings"]


def test_missing_persisted_broker_receipt_blocks(tmp_path):
    paths = fixtures(tmp_path)
    paths[2].write_text("")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_EMBEDDED_BROKER_LEDGER_MISMATCH" in result["findings"]


def test_unreserved_reject_with_live_routing_claim_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = {"mode": "PAPER", "decision": "REJECT_ORDER",
             "production": "ENABLED", "real_broker_routing": "ENABLED"}
    paths[-1].write_text(paths[-1].read_text() + json.dumps(event) + "\n")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert "BLOCK_EXECUTION_LIVE_ROUTING_CLAIM" in result["findings"]


def test_unreserved_reject_without_live_routing_claim_allowed(tmp_path):
    paths = fixtures(tmp_path)
    event = {"mode": "PAPER", "decision": "REJECT_ORDER", "production": "BLOCKED"}
    paths[-1].write_text(paths[-1].read_text() + json.dumps(event) + "\n")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is True
    assert result["operational_certified"] is False


def test_non_paper_accepted_execution_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = {"mode": "LIVE", "decision": "ACCEPT_SIMULATED_ORDER"}
    paths[-1].write_text(paths[-1].read_text() + json.dumps(event) + "\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_NON_PAPER_EXECUTION_ACCEPTANCE" in result["findings"]


def test_non_paper_filled_capacity_blocks(tmp_path):
    paths = fixtures(tmp_path)
    event = {"mode": "REAL", "decision": "REJECT_ORDER", "capacity_decision": "FILLED"}
    paths[-1].write_text(paths[-1].read_text() + json.dumps(event) + "\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_NON_PAPER_EXECUTION_ACCEPTANCE" in result["findings"]


def test_missing_order_id_detected_even_with_other_valid_acceptance(tmp_path):
    paths = fixtures(tmp_path)
    valid = json.loads(paths[-1].read_text())
    uncorrelated = dict(valid)
    uncorrelated.pop("capacity_order_id")
    paths[-1].write_text(json.dumps(valid)+"\n"+json.dumps(uncorrelated)+"\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_ACCEPTED_EXECUTION_UNCORRELATED" in result["findings"]


def test_rejected_without_reservation_remains_compatible(tmp_path):
    paths = fixtures(tmp_path)
    reject = {"mode": "PAPER", "decision": "REJECT_ORDER"}
    paths[-1].write_text(paths[-1].read_text()+json.dumps(reject)+"\n")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is True
    assert result["operational_certified"] is False


def test_duplicate_persisted_broker_receipt_blocks(tmp_path):
    paths = fixtures(tmp_path)
    receipt = paths[2].read_text()
    paths[2].write_text(receipt + receipt)
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert "BLOCK_DUPLICATE_PERSISTED_BROKER_RECEIPT" in result["findings"]


def test_distinct_order_receipt_does_not_trigger_duplicate_finding(tmp_path):
    paths = fixtures(tmp_path)
    receipt = json.loads(paths[2].read_text())
    receipt["order"]["capacity_order_id"] = "unrelated"
    paths[2].write_text(paths[2].read_text() + json.dumps(receipt) + "\n")
    result = audit_four_ledgers(*paths)
    assert "BLOCK_DUPLICATE_PERSISTED_BROKER_RECEIPT" not in result["findings"]


def test_malformed_broker_jsonl_fails_closed(tmp_path):
    paths = fixtures(tmp_path)
    paths[2].write_text("{invalid json\n")
    result = audit_four_ledgers(*paths)
    assert result["certified"] is False
    assert result["operational_certified"] is False
    assert "BLOCK_BROKER_LEDGER_RECHECK_UNAVAILABLE" in result["findings"]
