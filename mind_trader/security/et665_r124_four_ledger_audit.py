"""ET665.R124: fail-closed four-ledger PAPER audit, read-only.

This audit does not reconcile writes or authorize broker routing. It requires
the existing SQLite/session/broker audit and a matching execution decision.
"""
import json
from pathlib import Path
from et665_r122_paper_reconciliation import audit_paper_consistency


def audit_four_ledgers(sqlite_path, session_path, broker_path, execution_path):
    base = audit_paper_consistency(sqlite_path, session_path, broker_path)
    findings = list(base["findings"])
    try:
        session = json.loads(Path(session_path).read_text(encoding="utf-8"))
        events = [json.loads(line) for line in Path(execution_path).read_text(
            encoding="utf-8").splitlines() if line.strip()]
        if not events or any(not isinstance(event, dict) for event in events):
            raise ValueError("EMPTY_OR_INVALID_EXECUTION_LEDGER")
    except (OSError, ValueError, TypeError):
        return {**base, "certified": False,
                "findings": sorted(set(findings + ["BLOCK_EXECUTION_LEDGER_UNAVAILABLE"])),
                "scope": "OFFLINE_FOUR_LEDGER_ONLY"}

    seen = set()
    for event in events:
        if event.get("mode") != "PAPER":
            continue
        oid = event.get("capacity_order_id")
        if not isinstance(oid, str) or not oid:
            continue  # Early rejects need not have a reservation.
        if oid in seen:
            findings.append("BLOCK_DUPLICATE_EXECUTION_ORDER")
        seen.add(oid)
        decision = event.get("decision")
        capacity = event.get("capacity_decision")
        broker = event.get("paper_broker")
        if decision == "ACCEPT_SIMULATED_ORDER":
            if capacity != "FILLED" or not isinstance(broker, dict) or (
                broker.get("decision") != "PAPER_ORDER_ACCEPTED"
                or not isinstance(broker.get("fill"), dict)
                or broker["fill"].get("filled") is not True
            ):
                findings.append("BLOCK_EXECUTION_ACCEPTANCE_CONTRADICTION")
        elif capacity == "FILLED":
            findings.append("BLOCK_FILLED_EXECUTION_REJECTED")

    if base["certified"] and not seen:
        findings.append("BLOCK_MISSING_EXECUTION_CORRELATION")
    return {**base, "certified": not findings, "findings": sorted(set(findings)),
            "scope": "OFFLINE_FOUR_LEDGER_ONLY", "execution_order_count": len(seen)}
