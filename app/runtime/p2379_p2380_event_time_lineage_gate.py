from __future__ import annotations

import re
import hashlib
import hmac
from datetime import datetime
from typing import Any, Dict, List, Tuple

TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "H4", "D1"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("TIMESTAMP_MISSING")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("TIMESTAMP_INVALID") from exc
    return parsed


def _strict_index(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("INDEX_NOT_INTEGER")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"(0|[1-9][0-9]*)", value):
        return int(value)
    raise ValueError("INDEX_NOT_INTEGER")


def validate_event_bound_signal(signal: Dict[str, Any]) -> Tuple[bool, str]:
    """Fail closed unless a PAPER signal has verifiable event and raw-source lineage."""
    required = (
        "symbol", "timeframe", "event_time", "event_index", "event_id",
        "source_dataset_sha256", "source_row_sha256", "direction",
        "entry_time", "entry_index", "mode", "real_orders", "ftmo_real",
    )
    if not isinstance(signal, dict):
        return False, "SIGNAL_NOT_OBJECT"
    missing = [key for key in required if key not in signal or signal[key] in (None, "")]
    if missing:
        return False, "MISSING_LINEAGE:" + ",".join(missing)
    if str(signal["timeframe"]).upper() not in TIMEFRAMES:
        return False, "TIMEFRAME_INVALID"
    if not str(signal["symbol"]).strip() or not str(signal["event_id"]).strip():
        return False, "IDENTITY_INVALID"
    if not SHA256_RE.fullmatch(str(signal["source_dataset_sha256"])):
        return False, "DATASET_HASH_INVALID"
    if not SHA256_RE.fullmatch(str(signal["source_row_sha256"])):
        return False, "SOURCE_ROW_HASH_INVALID"
    if str(signal["direction"]).upper() not in {"BUY", "SELL", "BUY_INFERRED", "SELL_INFERRED"}:
        return False, "DIRECTION_INVALID"
    if signal["mode"] != "PAPER_ONLY" or signal["real_orders"] != "FORBIDDEN" or signal["ftmo_real"] != "FORBIDDEN":
        return False, "EXECUTION_MODE_FORBIDDEN"
    try:
        event_index = _strict_index(signal["event_index"])
        entry_index = _strict_index(signal["entry_index"])
        event_time = _timestamp(signal["event_time"])
        entry_time = _timestamp(signal["entry_time"])
    except (TypeError, ValueError) as exc:
        return False, str(exc) if str(exc) else "INDEX_OR_TIME_INVALID"
    if event_index < 0 or entry_index != event_index + 1:
        return False, "ENTRY_MUST_BE_IMMEDIATE_NEXT_BAR"
    if event_time.tzinfo is None or entry_time.tzinfo is None:
        return False, "TIMESTAMP_TIMEZONE_REQUIRED"
    if entry_time <= event_time:
        return False, "ENTRY_NOT_AFTER_EVENT_TIME"
    return True, "EVENT_LINEAGE_VALID_PAPER_ONLY"


def verify_source_hashes(signal: Dict[str, Any], dataset_bytes: bytes, row_bytes: bytes) -> Tuple[bool, str]:
    """Verify lineage against independently supplied original bytes; never trust declared hashes alone."""
    ok, reason = validate_event_bound_signal(signal)
    if not ok:
        return False, reason
    if not isinstance(dataset_bytes, bytes) or not isinstance(row_bytes, bytes):
        return False, "SOURCE_BYTES_REQUIRED"
    if not dataset_bytes or not row_bytes:
        return False, "SOURCE_BYTES_EMPTY"
    dataset_digest = hashlib.sha256(dataset_bytes).hexdigest()
    row_digest = hashlib.sha256(row_bytes).hexdigest()
    if not hmac.compare_digest(dataset_digest, signal["source_dataset_sha256"].lower()):
        return False, "DATASET_HASH_MISMATCH"
    if not hmac.compare_digest(row_digest, signal["source_row_sha256"].lower()):
        return False, "ROW_HASH_MISMATCH"
    return True, "SOURCE_HASHES_VERIFIED"


def validate_replay_promotion(evidence: Dict[str, Any]) -> Tuple[bool, str]:
    """Reject promotion of in-sample patch replay without independently verified OOS lineage."""
    if not isinstance(evidence, dict):
        return False, "EVIDENCE_NOT_OBJECT"
    if evidence.get("mode") != "PAPER_ONLY":
        return False, "PAPER_ONLY_REQUIRED"
    if evidence.get("real_orders") != "FORBIDDEN" or evidence.get("ftmo_real") != "FORBIDDEN":
        return False, "REAL_EXECUTION_FORBIDDEN"
    if evidence.get("independent_oos_certified") is not True:
        return False, "INDEPENDENT_OOS_NOT_CERTIFIED"
    if evidence.get("temporal_leakage_audit_pass") is not True:
        return False, "TEMPORAL_LEAKAGE_NOT_CLEARED"
    if evidence.get("source_lineage_verified") is not True:
        return False, "SOURCE_LINEAGE_NOT_VERIFIED"
    return False, "EXTERNAL_OOS_EVIDENCE_VERIFIER_REQUIRED"


def resolve_verified_next_bar_entry(
    signal: Dict[str, Any], candles: List[Dict[str, Any]],
    dataset_bytes: bytes, row_bytes: bytes,
) -> int:
    """Fail closed at the integration boundary unless both original hashes match."""
    ok, reason = verify_source_hashes(signal, dataset_bytes, row_bytes)
    if not ok:
        raise ValueError(reason)
    return resolve_next_bar_entry(signal, candles)


def resolve_next_bar_entry(signal: Dict[str, Any], candles: List[Dict[str, Any]]) -> int:
    """Resolve only the immediate next candle after the source event; never hash-select an entry."""
    ok, reason = validate_event_bound_signal(signal)
    if not ok:
        raise ValueError(reason)
    event_index = _strict_index(signal["event_index"])
    entry_index = _strict_index(signal["entry_index"])
    if entry_index != event_index + 1:
        raise ValueError("ENTRY_MUST_BE_IMMEDIATE_NEXT_BAR")
    if not isinstance(candles, list) or event_index >= len(candles) or entry_index >= len(candles):
        raise ValueError("NEXT_BAR_UNAVAILABLE")
    if not isinstance(candles[event_index], dict) or not isinstance(candles[entry_index], dict):
        raise ValueError("CANDLE_NOT_OBJECT")
    event_bar_time = _timestamp(str(candles[event_index].get("time", "")))
    entry_bar_time = _timestamp(str(candles[entry_index].get("time", "")))
    signal_event_time = _timestamp(signal["event_time"])
    signal_entry_time = _timestamp(signal["entry_time"])
    if event_bar_time.tzinfo is None or entry_bar_time.tzinfo is None:
        raise ValueError("CANDLE_TIMEZONE_REQUIRED")
    if event_bar_time != signal_event_time:
        raise ValueError("EVENT_BAR_TIMESTAMP_MISMATCH")
    if entry_bar_time != signal_entry_time or entry_bar_time <= event_bar_time:
        raise ValueError("ENTRY_BAR_TIMESTAMP_MISMATCH")
    return entry_index


__all__ = ["validate_event_bound_signal", "verify_source_hashes", "resolve_next_bar_entry", "resolve_verified_next_bar_entry", "validate_replay_promotion"]