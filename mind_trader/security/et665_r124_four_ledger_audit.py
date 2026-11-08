"""ET665.R124: fail-closed four-ledger PAPER audit, read-only.

This audit does not reconcile writes or authorize broker routing. It requires
the existing SQLite/session/broker audit and a matching execution decision.
"""
import json
import sqlite3
from pathlib import Path
from et665_r122_paper_reconciliation import audit_paper_consistency


def audit_four_ledgers(sqlite_path, session_path, broker_path, execution_path):
    base = audit_paper_consistency(sqlite_path, session_path, broker_path)
    findings = list(base["findings"])
    try:
        session = json.loads(Path(session_path).read_text(encoding="utf-8"))
        events = [json.loads(line) for line in Path(execution_path).read_text(
            encoding="utf-8").splitlines() if line.strip()]
        if not isinstance(session, dict) or not events or any(not isinstance(event, dict) for event in events):
            raise ValueError("EMPTY_OR_INVALID_EXECUTION_LEDGER")
    except (OSError, ValueError, TypeError):
        return {**base, "certified": False, "operational_certified": False,
                "findings": sorted(set(findings + ["BLOCK_EXECUTION_LEDGER_UNAVAILABLE"])),
                "scope": "OFFLINE_FOUR_LEDGER_ONLY"}

    seen = set()
    accepted_ids = set()
    accepted_embedded = {}
    for event in events:
        if event.get("mode") != "PAPER":
            continue
        oid = event.get("capacity_order_id")
        if not isinstance(oid, str) or not oid:
            continue  # Early rejects need not have a reservation.
        if oid in seen:
            findings.append("BLOCK_DUPLICATE_EXECUTION_ORDER")
        seen.add(oid)
        if event.get("session_id") not in (None, session.get("session_id")):
            findings.append("BLOCK_EXECUTION_SESSION_MISMATCH")
        if event.get("production") not in (None, "BLOCKED") or event.get("real_broker_routing") not in (None, "DISABLED"):
            findings.append("BLOCK_EXECUTION_LIVE_ROUTING_CLAIM")
        decision = event.get("decision")
        capacity = event.get("capacity_decision")
        broker = event.get("paper_broker")
        if decision == "ACCEPT_SIMULATED_ORDER":
            accepted_ids.add(oid)
            accepted_embedded[oid] = broker
            broker_order = broker.get("order") if isinstance(broker, dict) else None
            if not isinstance(broker_order, dict) or broker_order.get("capacity_order_id") != oid or broker_order.get("session_id") != session.get("session_id"):
                findings.append("BLOCK_EMBEDDED_BROKER_ORDER_MISMATCH")
            if capacity != "FILLED" or not isinstance(broker, dict) or (
                broker.get("decision") != "PAPER_ORDER_ACCEPTED"
                or not isinstance(broker.get("fill"), dict)
                or broker["fill"].get("filled") is not True
            ):
                findings.append("BLOCK_EXECUTION_ACCEPTANCE_CONTRADICTION")
        elif capacity == "FILLED":
            findings.append("BLOCK_FILLED_EXECUTION_REJECTED")

    try:
        broker_events = [json.loads(line) for line in Path(broker_path).read_text(
            encoding="utf-8").splitlines() if line.strip()]
        actual_broker = {}
        for broker_event in broker_events:
            if not isinstance(broker_event, dict):
                raise ValueError("INVALID_BROKER_EVENT")
            order = broker_event.get("order")
            if isinstance(order, dict) and order.get("session_id") == session.get("session_id"):
                oid = order.get("capacity_order_id")
                if isinstance(oid, str) and oid:
                    actual_broker[oid] = broker_event
        for oid, embedded in accepted_embedded.items():
            if actual_broker.get(oid) != embedded:
                findings.append("BLOCK_EMBEDDED_BROKER_LEDGER_MISMATCH")
    except (OSError, ValueError, TypeError):
        findings.append("BLOCK_BROKER_LEDGER_RECHECK_UNAVAILABLE")

    try:
        with sqlite3.connect(f"file:{Path(sqlite_path).resolve()}?mode=ro", uri=True) as db:
            filled_ids = {oid for sid, oid in db.execute(
                "SELECT session_id, order_id FROM reservations WHERE state = 'FILLED'"
            ) if sid == session.get("session_id")}
    except (sqlite3.Error, OSError):
        filled_ids = set()
        findings.append("BLOCK_RESERVATION_RECHECK_UNAVAILABLE")
    if len(accepted_ids) != len([e for e in events if e.get("mode") == "PAPER" and e.get("decision") == "ACCEPT_SIMULATED_ORDER"]):
        findings.append("BLOCK_ACCEPTED_EXECUTION_UNCORRELATED")
    if accepted_ids - filled_ids:
        findings.append("BLOCK_EXECUTION_ACCEPTED_WITHOUT_FILLED_RESERVATION")
    if filled_ids - accepted_ids:
        findings.append("BLOCK_MISSING_EXECUTION_CORRELATION")
    if base["certified"] and not seen:
        findings.append("BLOCK_MISSING_EXECUTION_CORRELATION")
    return {**base, "certified": not findings, "findings": sorted(set(findings)),
            "operational_certified": False, "production": "BLOCKED",
            "scope": "OFFLINE_FOUR_LEDGER_ONLY", "execution_order_count": len(seen)}
