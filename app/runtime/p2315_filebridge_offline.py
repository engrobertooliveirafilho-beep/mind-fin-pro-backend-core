"""Offline PAPER-only FileBridge lifecycle: clearing a file is not consumption.

No terminal, broker, filesystem mutation or real-order API is called.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

@dataclass(frozen=True)
class PaperSignal:
    symbol: str
    side: str
    lot: Decimal
    signal_id: str
    timestamp: str

def parse_paper_signal(content):
    if not isinstance(content,str):
        raise ValueError("SIGNAL_NOT_TEXT")
    parts=content.strip().split(",")
    if len(parts)!=5:
        raise ValueError("SIGNAL_SCHEMA_INVALID")
    symbol,side,lot_text,signal_id,timestamp=parts
    if symbol!="GER40" or side not in ("BUY","SELL"):
        raise ValueError("UNAUTHORIZED_SYMBOL_OR_SIDE")
    try:
        lot=Decimal(lot_text)
    except InvalidOperation:
        raise ValueError("INVALID_LOT") from None
    if lot!=Decimal("0.01") or not (signal_id=="P2311_ACTIVE_TEST" or (signal_id.startswith("P2316_") and len(signal_id)==18 and all(c in "0123456789abcdef" for c in signal_id[6:]))):
        raise ValueError("UNAUTHORIZED_LOT_OR_SIGNAL")
    if not timestamp or len(timestamp)!=19 or timestamp[10]!="T":
        raise ValueError("INVALID_TIMESTAMP")
    return PaperSignal(symbol,side,lot,signal_id,timestamp)

def reconcile_clear(before_content, *, after_exists, backup_content, terminal_receipt=None):
    signal=parse_paper_signal(before_content)
    if after_exists is not False or backup_content!=before_content:
        raise ValueError("CLEAR_NOT_VERIFIED")
    # Never infer terminal receipt from a cleared file, a backup, or log-hit counts.
    return {"status":"FILE_CLEARED_CONSUMPTION_UNVERIFIED",
            "signal_id":signal.signal_id,"backup_preserved":True,
            "terminal_read_proven":False,"execution_proven":False,
            "orders_authorized":0,"e2e_certified":False}
