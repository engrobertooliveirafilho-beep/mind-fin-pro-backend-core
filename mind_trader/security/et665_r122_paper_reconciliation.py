"""ET665.R122: read-only PAPER reconciliation. Never sends orders or repairs ledgers.

A reservation with an uncertain outcome is always a blocker, not a reason to
release capacity. Session trade counters cannot prove order-level settlement.
"""
import json
import sqlite3
from pathlib import Path


def audit_paper_consistency(sqlite_path, session_path, broker_ledger_path):
    findings = []
    try:
        with sqlite3.connect(f"file:{Path(sqlite_path).resolve()}?mode=ro", uri=True) as db:
            rows = db.execute(
                "SELECT session_id, order_id, state FROM reservations"
            ).fetchall()
        session = json.loads(Path(session_path).read_text(encoding="utf-8"))
        if not isinstance(session, dict) or not isinstance(session.get("session_id"), str) or not session["session_id"].strip():
            raise ValueError("INVALID_SESSION")
        broker_events = []
        for line in Path(broker_ledger_path).read_text(encoding="utf-8").splitlines():
            if line.strip():
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError("INVALID_BROKER_EVENT")
                broker_events.append(event)
    except (OSError, sqlite3.Error, ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"certified": False, "findings": ["BLOCK_INPUT_UNAVAILABLE_OR_CORRUPT"],
                "error_type": type(exc).__name__, "production": "BLOCKED"}

    if not rows and not broker_events:
        findings.append("BLOCK_NO_ORDER_LEVEL_EVIDENCE")
    if session.get("status") not in ("OPEN", "CLOSED"):
        findings.append("BLOCK_INVALID_SESSION_STATUS")
    if type(session.get("trades")) is not int or session["trades"] < 0:
        findings.append("BLOCK_INVALID_SESSION_TRADE_COUNT")
    reservations = {}
    for sid, oid, state in rows:
        if not isinstance(sid, str) or not sid or not isinstance(oid, str) or not oid or state not in ("RESERVED", "FILLED", "REJECTED"):
            findings.append("BLOCK_INVALID_RESERVATION")
        if (sid, oid) in reservations:
            findings.append("BLOCK_DUPLICATE_RESERVATION")
        reservations[(sid, oid)] = state
        if sid != session["session_id"]:
            findings.append("BLOCK_SESSION_MISMATCH")
        if state == "RESERVED":
            findings.append("BLOCK_UNCERTAIN_RESERVATION")

    seen = set()
    accepted = set()
    for event in broker_events:
        if (event.get("production") not in (None, "BLOCKED")
                or event.get("live") not in (None, "FORBIDDEN")
                or event.get("real_broker_routing") not in (None, "DISABLED")
                or event.get("broker") not in (None, "PAPER_INTERNAL")):
            findings.append("BLOCK_PERSISTED_BROKER_LIVE_ROUTING_CLAIM")
        order = event.get("order")
        if isinstance(order, dict) and (order.get("mode") not in (None, "PAPER")
                or order.get("production") not in (None, "BLOCKED")
                or order.get("real_broker_routing") not in (None, "DISABLED")):
            findings.append("BLOCK_PERSISTED_BROKER_ORDER_LIVE_CLAIM")
        oid = order.get("capacity_order_id") if isinstance(order, dict) else None
        sid = order.get("session_id") if isinstance(order, dict) else None
        if not isinstance(oid, str) or not oid or not isinstance(sid, str) or not sid:
            findings.append("BLOCK_UNCORRELATED_BROKER_EVENT")
            continue
        key = (sid, oid)
        if key in seen:
            findings.append("BLOCK_DUPLICATE_BROKER_EVENT")
        seen.add(key)
        if key not in reservations:
            findings.append("BLOCK_ORPHAN_BROKER_EVENT")
        if event.get("decision") not in ("PAPER_ORDER_ACCEPTED", "PAPER_ORDER_REJECTED", "PAPER_ORDER_REJECTED_INVALID_PAYLOAD", "PAPER_ORDER_REJECTED_FILL"):
            findings.append("BLOCK_UNKNOWN_BROKER_DECISION")
        if event.get("decision") != "PAPER_ORDER_ACCEPTED" and isinstance(event.get("fill"), dict) and event["fill"].get("filled") is True:
            findings.append("BLOCK_REJECTED_BROKER_WITH_CONFIRMED_FILL")
        if event.get("decision") != "PAPER_ORDER_ACCEPTED" and event.get("order_status") == "PAPER_FILLED_SIMULATED":
            findings.append("BLOCK_REJECTED_BROKER_WITH_FILLED_STATUS")
        if event.get("decision") == "PAPER_ORDER_ACCEPTED" and event.get("order_status") not in (None, "PAPER_FILLED_SIMULATED"):
            findings.append("BLOCK_ACCEPTED_BROKER_WITH_CONTRADICTORY_STATUS")
        if event.get("decision") == "PAPER_ORDER_ACCEPTED" and not isinstance(event.get("order"), dict):
            findings.append("BLOCK_ACCEPTED_BROKER_WITHOUT_ORDER")
        if event.get("decision") == "PAPER_ORDER_ACCEPTED":
            fill = event.get("fill")
            if not isinstance(fill, dict) or fill.get("filled") is not True:
                findings.append("BLOCK_UNCONFIRMED_FILL")
            else:
                accepted.add(key)
                if reservations.get(key) != "FILLED":
                    findings.append("BLOCK_ACCEPTED_NOT_FINALIZED")
        elif reservations.get(key) == "FILLED":
            findings.append("BLOCK_FILLED_WITHOUT_ACCEPTANCE")

    for key, state in reservations.items():
        if state == "FILLED" and key not in accepted:
            findings.append("BLOCK_FILLED_WITHOUT_BROKER_EVIDENCE")
    if type(session.get("trades")) is int and session["trades"] != sum(
        state == "FILLED" for (sid, _), state in reservations.items()
        if sid == session["session_id"]
    ):
        findings.append("BLOCK_SESSION_TRADE_COUNT_MISMATCH")
    return {"certified": not findings, "findings": sorted(set(findings)),
            "reservation_count": len(rows), "broker_event_count": len(broker_events),
            "production": "BLOCKED", "scope": "OFFLINE_SINGLE_SESSION_ONLY"}
