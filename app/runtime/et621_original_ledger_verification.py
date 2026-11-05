"""Offline original-ledger verification; caller must supply independently trusted expected hash."""
import csv
import hashlib
import io
from decimal import Decimal, InvalidOperation

class LedgerBlocked(ValueError):
    pass

def number(value):
    if isinstance(value, (bool, float)):
        raise LedgerBlocked("unsafe numeric representation")
    try:
        n = Decimal(str(value))
    except (ValueError, InvalidOperation) as exc:
        raise LedgerBlocked("invalid decimal") from exc
    if not n.is_finite():
        raise LedgerBlocked("nonfinite decimal")
    return n

def verify_original_csv(raw, expected_sha256, *, edge_id):
    if not isinstance(raw, bytes) or not raw:
        raise LedgerBlocked("original raw CSV bytes required")
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise LedgerBlocked("trusted expected SHA256 required")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256.lower():
        raise LedgerBlocked("SHA256 mismatch")
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise LedgerBlocked("unsupported CSV encoding") from exc
    reader = csv.DictReader(io.StringIO(content, newline=""))
    if reader.fieldnames is None or not {"trade_id", "edge_id", "pnl"}.issubset(reader.fieldnames):
        raise LedgerBlocked("missing trade identity/PnL columns")
    rows = list(reader)
    if not rows:
        raise LedgerBlocked("empty ledger")
    seen = set()
    for row in rows:
        if not row["trade_id"] or row["trade_id"] in seen or row["edge_id"] != edge_id:
            raise LedgerBlocked("duplicate/missing trade or mismatched edge")
        seen.add(row["trade_id"])
        number(row["pnl"])
    return {"sha256": digest, "edge_id": edge_id, "rows": rows}

def convert_points_to_account_currency(verified, *, symbol, volume_lots, money_per_point_per_lot, contract_source_sha256, account_currency, source_currency):
    if not verified or not verified.get("rows") or not verified.get("sha256"):
        raise LedgerBlocked("verified ledger required")
    if not symbol or not account_currency or account_currency != source_currency:
        raise LedgerBlocked("unreconciled currency conversion")
    if not isinstance(contract_source_sha256, str) or len(contract_source_sha256) != 64:
        raise LedgerBlocked("contract source hash required")
    volume = number(volume_lots)
    rate = number(money_per_point_per_lot)
    if volume <= 0 or rate <= 0:
        raise LedgerBlocked("invalid lot or point value")
    return [{"trade_id": r["trade_id"], "edge_id": r["edge_id"], "pnl": str(number(r["pnl"]) * volume * rate), "pnl_unit": "account_currency", "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN"} for r in verified["rows"]]
