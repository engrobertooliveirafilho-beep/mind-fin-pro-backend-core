"""ET665 R35: 60-minute persistent, offline, supervised PAPER rehearsal.

One process, one durable session, multiple unique historical candidates. No live APIs.
Exit code nonzero on any mismatch; checkpoint JSON and SHA-256 are written locally.
"""
import argparse
import hashlib
import json
import math
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tests.test_et665_m8_gateway_e2e import M8GatewayE2E
from mind_trader.app.backtest.p2405_paper_gateway import replay_financially_verified_candidate
from mind_trader.app.backtest.p2405_paper_settlement import settle_historical_paper_exit
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.execution.paper_session import PaperTradingSessionManager


def demand(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def rows(path):
    p = Path(path)
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()] if p.exists() else []


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--minutes", type=int, default=60)
    args = ap.parse_args()
    demand(args.minutes in (0, 60), "ONLY_PREFLIGHT_OR_60_MINUTES_ALLOWED")
    evidence = Path(args.evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    fixture = M8GatewayE2E(methodName="test_no_authorization_no_order")
    fixture.setUp()
    # The test fixture owns the single persistent state throughout the rehearsal.
    selected = []
    for event in fixture.research["events"]:
        if event.get("side") == "BUY" and event.get("candidate_id") not in {x["candidate_id"] for x in selected}:
            selected.append(event)
        if len(selected) == 2:
            break
    demand(len(selected) == 2, "INSUFFICIENT_UNIQUE_HISTORICAL_CANDIDATES")
    expected = {}
    start = time.monotonic()
    outcome = {"result": "FAIL", "completed_checkpoints": 0, "orders": 0,
               "production": "BLOCKED", "real_orders": "FORBIDDEN"}
    try:
        for minute in range(args.minutes + 1):
            # Fresh objects prove restart/recovery against the SAME durable files.
            manager = PaperTradingSessionManager(str(fixture.session), str(fixture.day), str(fixture.config))
            gateway = ExecutionGateway(ledger_path=str(fixture.execution),
                ftmo_config_path=str(fixture.config), paper_session_path=str(fixture.session),
                paper_day_ledger_path=str(fixture.day), paper_broker_ledger_path=str(fixture.broker))
            if minute in (0, 30):
                candidate = selected[len(expected)]
                pre = gateway.paper.reconcile_paper_fills(str(fixture.broker))
                demand(pre.get("decision") == "PAPER_RECONCILIATION_CLEAN", "PRE_ENTRY_RECONCILIATION")
                placed = replay_financially_verified_candidate(candidate, gateway,
                    quantity=1, quote_to_account_rate=1, contract_multiplier=1,
                    risk_amount=10, stop_distance=1, regime_report=fixture.regime,
                    genome=fixture.genome, authorize_offline_replay=True)
                demand(placed.get("decision") == "ACCEPT_SIMULATED_ORDER", "ORDER_NOT_ACCEPTED:" + repr(placed))
                rid = placed["reservation_id"]
                demand(rid not in expected, "DUPLICATE_RESERVATION")
                expected[rid] = None
                # Simulate process restart between fill and recovery.
                manager = PaperTradingSessionManager(str(fixture.session), str(fixture.day), str(fixture.config))
                demand(manager.reconcile_paper_fills(str(fixture.broker))["decision"] == "BLOCK_UNSETTLED_BROKER_FILL",
                       "UNSETTLED_FILL_NOT_DETECTED")
                demand(manager.recover_interrupted_paper_fills(str(fixture.broker))["decision"] in
                       ("PAPER_FILLS_ACKNOWLEDGED", "PAPER_RECOVERY_NO_CHANGE"), "RECOVERY_FAILED")
                # Same unique candidate must never generate a second broker fill.
                duplicate = replay_financially_verified_candidate(candidate, gateway,
                    quantity=1, quote_to_account_rate=1, contract_multiplier=1,
                    risk_amount=10, stop_distance=1, regime_report=fixture.regime,
                    genome=fixture.genome, authorize_offline_replay=True)
                demand(duplicate.get("decision") != "ACCEPT_SIMULATED_ORDER", "DUPLICATE_ACCEPTED")
                broker_row = [r for r in rows(fixture.broker) if r.get("decision") == "PAPER_ORDER_ACCEPTED"
                              and r.get("order", {}).get("reservation_id") == rid]
                demand(len(broker_row) == 1, "BROKER_FILL_NOT_UNIQUE")
                order = broker_row[0]["order"]
                demand(all(order.get(k) == 1 for k in
                           ("quantity", "quote_to_account_rate", "contract_multiplier")), "DURABLE_UNITS_DRIFT")
                settled = settle_historical_paper_exit(manager, broker_ledger_path=str(fixture.broker),
                    reservation_id=rid, entry_ts=candidate["fill_ts"],
                    exit_ts="2027-01-01T00:00:00", exit_close=broker_row[0]["fill"]["fill_price"],
                    quantity=order["quantity"], quote_to_account_rate=order["quote_to_account_rate"],
                    settlement_evidence_path=evidence / ("settlement_" + str(len(expected)) + ".json"),
                    authorize_offline_replay=True)
                demand(settled.get("decision") == "M9_HISTORICAL_PAPER_SETTLED", "SETTLEMENT_FAILED:" + repr(settled))
                expected[rid] = settled["net_account"]
                demand(manager.settle_paper_order(rid, settled["net_account"])["decision"] !=
                       "PAPER_RESERVATION_SETTLED", "DOUBLE_SETTLEMENT")
            broker = [r for r in rows(fixture.broker) if r.get("decision") == "PAPER_ORDER_ACCEPTED"]
            execution = [r for r in rows(fixture.execution) if r.get("decision") == "ACCEPT_SIMULATED_ORDER"]
            day = [r for r in rows(fixture.day) if r.get("type") == "PAPER_RESERVATION_SETTLED"]
            session = manager._read_session()
            demand(session is not None and session["status"] == "OPEN", "SESSION_INVALID")
            demand(len(broker) == len(execution) == len(day) == len(expected), "THREE_LEDGER_COUNT_DRIFT")
            ids_b = [r["order"]["reservation_id"] for r in broker]
            ids_e = [r["paper_reservation_id"] for r in execution]
            ids_d = [r["reservation_id"] for r in day]
            demand(len(set(ids_b)) == len(ids_b) and set(ids_b) == set(ids_e) == set(ids_d) == set(expected),
                   "THREE_LEDGER_ID_DRIFT")
            demand(session["trades"] == len(expected) and not session.get("pending_paper_orders"),
                   "SESSION_TRADE_OR_PENDING_DRIFT")
            demand(session["trades"] <= session["max_daily_trades"], "FTMO_TRADE_LIMIT_BREACHED")
            demand(math.isclose(session["daily_pnl"], sum(expected.values()), rel_tol=1e-9, abs_tol=1e-8),
                   "SESSION_PNL_DRIFT")
            demand(all(math.isclose(r["pnl"], expected[r["reservation_id"]], rel_tol=1e-9, abs_tol=1e-8)
                       for r in day), "DAY_LEDGER_PNL_DRIFT")
            demand(manager.reconcile_paper_fills(str(fixture.broker))["decision"] == "PAPER_RECONCILIATION_CLEAN",
                   "POST_SETTLEMENT_RECONCILIATION")
            checkpoint = {"minute": minute, "elapsed_seconds": round(time.monotonic()-start, 3),
                          "session_id": session["session_id"], "trades": session["trades"],
                          "daily_pnl": session["daily_pnl"], "broker_fills": len(broker),
                          "execution_accepts": len(execution), "settlements": len(day),
                          "session_sha256": digest(fixture.session),
                          "broker_sha256": digest(fixture.broker),
                          "execution_sha256": digest(fixture.execution),
                          "day_sha256": digest(fixture.day)}
            (evidence / ("checkpoint_%03d.json" % minute)).write_text(
                json.dumps(checkpoint, sort_keys=True), encoding="utf-8")
            outcome["completed_checkpoints"] = minute+1
            outcome["orders"] = len(expected)
            if minute < args.minutes:
                wait = start + (minute+1)*60 - time.monotonic()
                if wait > 0:
                    time.sleep(wait)
        if args.minutes == 60:
            demand(time.monotonic()-start >= 3600, "DURATION_SHORT")
        else:
            outcome["preflight_only"] = True
        outcome["result"] = "PASS"
    except BaseException as exc:
        outcome["failure"] = repr(exc)
        raise
    finally:
        outcome["elapsed_seconds"] = round(time.monotonic()-start, 3)
        (evidence/"RESULT.json").write_text(json.dumps(outcome, sort_keys=True), encoding="utf-8")
        hashes = {p.name: digest(p) for p in evidence.iterdir() if p.is_file() and p.name != "SHA256.json"}
        (evidence/"SHA256.json").write_text(json.dumps(hashes, sort_keys=True), encoding="utf-8")
        fixture.doCleanups()


if __name__ == "__main__":
    main()
