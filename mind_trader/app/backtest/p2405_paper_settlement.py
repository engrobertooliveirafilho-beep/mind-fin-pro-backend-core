"""ET665 M9: offline historical exit accounting for existing PAPER reservations.

Exit is the close of a supplied, chronologically later historical candle.
Price units and quote-to-account conversion are explicit; never invent FX rates.
This module cannot submit orders or access live brokers.
"""
import json
import math
from pathlib import Path
from mind_trader.app.execution.paper_session import PaperTradingSessionManager


def _positive(x):
    return type(x) in (int, float) and math.isfinite(x) and x > 0


def settle_historical_paper_exit(manager, *, broker_ledger_path, reservation_id,
                                 entry_ts, exit_ts, exit_close, quantity,
                                 quote_to_account_rate, settlement_evidence_path,
                                 authorize_offline_replay=False):
    """Settle an accepted PAPER fill once, with existing session locks.

    Commission is treated as a per-unit per-side amount in quote currency.
    This explicit convention must be verified against the source cost ruleset.
    """
    blocked = {"decision": "BLOCK_M9_EXIT", "production": "BLOCKED",
               "real_broker_routing": "DISABLED", "reservation_id": reservation_id}
    if not authorize_offline_replay or not isinstance(manager, PaperTradingSessionManager):
        return dict(blocked, reason="REPLAY_NOT_AUTHORIZED")
    if not isinstance(reservation_id, str) or not reservation_id or not isinstance(entry_ts, str) or not isinstance(exit_ts, str) or entry_ts >= exit_ts:
        return dict(blocked, reason="INVALID_CHRONOLOGY_OR_RESERVATION")
    if not all(_positive(x) for x in (exit_close, quantity, quote_to_account_rate)):
        return dict(blocked, reason="INVALID_PRICE_SIZE_OR_CONVERSION")
    evidence = Path(settlement_evidence_path)
    if evidence.exists():
        return dict(blocked, reason="SETTLEMENT_EVIDENCE_ALREADY_EXISTS")
    try:
        rows = [json.loads(x) for x in Path(broker_ledger_path).read_text(encoding="utf-8").splitlines() if x.strip()]
    except (OSError, ValueError, UnicodeError):
        return dict(blocked, reason="INVALID_BROKER_LEDGER")
    accepted = [r for r in rows if r.get("decision") == "PAPER_ORDER_ACCEPTED" and
                isinstance(r.get("order"), dict) and r["order"].get("reservation_id") == reservation_id]
    if len(accepted) != 1:
        return dict(blocked, reason="BROKER_FILL_NOT_UNIQUE")
    record = accepted[0]
    order, fill = record["order"], record.get("fill")
    if not isinstance(fill, dict) or fill.get("filled") is not True or not _positive(fill.get("fill_price")):
        return dict(blocked, reason="INVALID_DURABLE_FILL")
    if record.get("production") != "BLOCKED" or record.get("live") != "FORBIDDEN" or record.get("real_broker_routing") != "DISABLED":
        return dict(blocked, reason="UNSAFE_BROKER_RECORD")
    side = order.get("side")
    if side not in ("BUY", "SELL"):
        return dict(blocked, reason="INVALID_SIDE")
    cfg, validation = __import__("mind_trader.app.risk.ftmo_ruleset",fromlist=["load_ftmo_config"]).load_ftmo_config(manager.ftmo_config_path)
    if not cfg or not validation.get("valid") or not all(
        type(cfg.get(k)) in (int, float) and math.isfinite(cfg[k]) and cfg[k] >= 0
        for k in ("spread", "slippage", "commission")
    ):
        return dict(blocked, reason="INVALID_FTMO_COSTS")
    if not all(abs(float(fill.get(k, float("nan"))) - float(cfg[k])) <= 1e-12
               for k in ("spread", "slippage", "commission")):
        return dict(blocked, reason="BROKER_COST_DRIFT")
    friction = cfg["spread"] / 2 + cfg["slippage"]
    exit_price = float(exit_close) - friction if side == "BUY" else float(exit_close) + friction
    if not _positive(exit_price):
        return dict(blocked, reason="INVALID_EXIT_FILL")
    signed_move = exit_price - fill["fill_price"] if side == "BUY" else fill["fill_price"] - exit_price
    gross_quote = signed_move * quantity
    commission_quote = 2 * cfg["commission"] * quantity
    net_account = (gross_quote - commission_quote) * quote_to_account_rate
    if not math.isfinite(net_account):
        return dict(blocked, reason="NONFINITE_NET_PNL")
    # Recovery acknowledges the durable broker fill but does NOT settle it.
    recovery = manager.recover_interrupted_paper_fills(broker_ledger_path)
    if recovery.get("decision") not in ("PAPER_FILLS_ACKNOWLEDGED", "PAPER_RECOVERY_NO_CHANGE"):
        return dict(blocked, reason="RECOVERY_BLOCKED", recovery=recovery.get("decision"))
    state = manager._read_session()
    pending = state.get("pending_paper_orders", []) if state else []
    if sum(x.get("id") == reservation_id and x.get("fill_recovered") is True for x in pending) != 1:
        return dict(blocked, reason="RESERVATION_NOT_RECOVERED")
    # The durable session settlement is the authority for exactly-once accounting.
    settled = manager.settle_paper_order(reservation_id, net_account)
    if settled.get("decision") != "PAPER_RESERVATION_SETTLED":
        return dict(blocked, reason="SETTLEMENT_REJECTED", settlement=settled.get("decision"))
    result = {"decision": "M9_HISTORICAL_PAPER_SETTLED", "production": "BLOCKED",
              "real_broker_routing": "DISABLED", "reservation_id": reservation_id,
              "entry_ts": entry_ts, "exit_ts": exit_ts, "entry_fill": fill["fill_price"],
              "exit_close": exit_close, "exit_fill": exit_price,
              "quantity": quantity, "quote_to_account_rate": quote_to_account_rate,
              "gross_quote": gross_quote, "commission_quote": commission_quote,
              "net_account": net_account, "costs": {k:cfg[k] for k in ("spread","slippage","commission")}}
    # Evidence is supplementary: a failed write must NOT trigger a second settlement.
    try:
        evidence.parent.mkdir(parents=True, exist_ok=True)
        with evidence.open("x", encoding="utf-8") as f:
            json.dump(result, f, sort_keys=True)
    except OSError:
        return dict(result, evidence_write="FAILED_SESSION_SETTLEMENT_IS_AUTHORITATIVE")
    return result
