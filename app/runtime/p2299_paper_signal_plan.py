"""P2299 PAPER signal-plan validator. No broker adapter, no execution path."""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

ALLOWED_FAMILIES = frozenset(("LIQUIDITY_SWEEP_REVERSAL", "VWAP_REVERSION"))
ALLOWED_CONFIRMATIONS = frozenset(("MTF_REQUIRED", "VOLATILITY_REQUIRED"))
REQUIRED_FIELDS = frozenset(("signal_id_template", "dedup_key", "symbol", "timeframe", "family", "confirmation", "exit_model", "lot", "mode", "real_orders", "ftmo_real", "order_format", "candle_lock", "max_signal_candle", "max_trades_day", "max_trades_edge_day", "source_final_status", "source_segments_passed", "status"))

def validate_plan(rows):
    if not isinstance(rows, (list, tuple)) or len(rows) != 4:
        raise ValueError("P2299_INVALID_PLAN_SIZE")
    keys = set()
    families = Counter()
    confirmations = Counter()
    for row in rows:
        if not isinstance(row, dict) or not REQUIRED_FIELDS.issubset(row):
            raise ValueError("P2299_INVALID_PLAN_ROW")
        if any(row.get(k) != v for k, v in {
            "symbol": "GER40", "timeframe": "H1", "exit_model": "TIME_EXIT",
            "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
            "order_format": "SYMBOL,ACTION,LOT,SIGNAL_ID,TIMESTAMP",
            "candle_lock": "CLOSED_H1", "source_final_status": "FINAL_APPROVED",
            "status": "PAPER_SIGNAL_PLAN_READY"}.items()):
            raise ValueError("P2299_UNSAFE_PLAN")
        if row["family"] not in ALLOWED_FAMILIES or row["confirmation"] not in ALLOWED_CONFIRMATIONS:
            raise ValueError("P2299_UNKNOWN_STRATEGY")
        try:
            lot = Decimal(str(row["lot"]))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("P2299_INVALID_LOT") from None
        if not lot.is_finite() or lot != Decimal("0.01"):
            raise ValueError("P2299_INVALID_LOT")
        if any(str(row[k]) != v for k, v in {
            "max_signal_candle": "1", "max_trades_day": "6",
            "max_trades_edge_day": "2", "source_segments_passed": "3"}.items()):
            raise ValueError("P2299_INVALID_LIMIT")
        key = row["dedup_key"]
        if not isinstance(key, str) or not re.fullmatch(r"[0-9a-f]{16}", key) or row["signal_id_template"] != "P2299_" + key[:12] or key in keys:
            raise ValueError("P2299_INVALID_DEDUP_KEY")
        keys.add(key)
        families[row["family"]] += 1
        confirmations[row["confirmation"]] += 1
    if any(families[x] != 2 for x in ALLOWED_FAMILIES) or any(confirmations[x] != 2 for x in ALLOWED_CONFIRMATIONS):
        raise ValueError("P2299_INCOMPLETE_PLAN")
    return {"status": "PAPER_PLAN_VALIDATED_NOT_CERTIFIED", "rows": 4, "unique_keys": 4, "independent_edges_certified": 0, "broker_orders": 0}

def paper_signal(row, candle, action, *, seen_keys, daily_count, edge_daily_count):
    """Return a non-executable observation record only; never a broker order."""
    validate_plan_row = dict(row)
    if any(validate_plan_row.get(k) != v for k, v in {"mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN", "symbol": "GER40", "timeframe": "H1", "exit_model": "TIME_EXIT", "candle_lock": "CLOSED_H1", "max_signal_candle": 1, "max_trades_day": 6, "max_trades_edge_day": 2}.items()) or validate_plan_row.get("family") not in ALLOWED_FAMILIES or validate_plan_row.get("confirmation") not in ALLOWED_CONFIRMATIONS:
        raise ValueError("P2299_UNSAFE_PLAN")
    try:
        lot = Decimal(str(validate_plan_row.get("lot")))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("P2299_INVALID_LOT") from None
    if not lot.is_finite() or lot != Decimal("0.01"):
        raise ValueError("P2299_INVALID_LOT")
    if not isinstance(candle, dict) or candle.get("closed") is not True or candle.get("timeframe") != "H1" or candle.get("symbol") != "GER40":
        raise ValueError("P2299_OPEN_OR_WRONG_CANDLE")
    if action not in ("BUY", "SELL"):
        raise ValueError("P2299_INVALID_ACTION")
    timestamp = candle.get("timestamp")
    if not isinstance(timestamp, str):
        raise ValueError("P2299_INVALID_TIMESTAMP")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise ValueError("P2299_INVALID_TIMESTAMP") from None
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.minute != 0 or parsed.second != 0 or parsed.microsecond != 0:
        raise ValueError("P2299_INVALID_TIMESTAMP")
    if not isinstance(daily_count, int) or isinstance(daily_count, bool) or not isinstance(edge_daily_count, int) or isinstance(edge_daily_count, bool) or daily_count < 0 or edge_daily_count < 0:
        raise ValueError("P2299_INVALID_COUNTER")
    if daily_count >= 6 or edge_daily_count >= 2:
        raise ValueError("P2299_DAILY_LIMIT")
    if not isinstance(seen_keys, (set, frozenset)):
        raise ValueError("P2299_INVALID_SEEN_KEYS")
    key = (row.get("dedup_key"), parsed.isoformat())
    if key in seen_keys or ("CANDLE", parsed.isoformat()) in seen_keys:
        raise ValueError("P2299_DUPLICATE_CANDLE")
    return {"status": "PAPER_OBSERVATION_ONLY", "symbol": "GER40", "action": action,
            "candle": parsed.isoformat(), "dedup_key": key, "lot_reference": "0.01",
            "broker_order": None, "real_orders": "FORBIDDEN"}
