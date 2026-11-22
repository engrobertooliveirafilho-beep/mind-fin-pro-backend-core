"""P2302 historical PAPER forward audit; never emits an MT5 command."""
from collections import Counter
from decimal import Decimal, InvalidOperation

def audit_paper_forward(rows, state):
    if not isinstance(rows, (list, tuple)) or not isinstance(state, dict):
        raise ValueError("P2302_INVALID_INPUT")
    if state.get("mode") != "PAPER_ONLY" or state.get("real_orders") != "FORBIDDEN" or state.get("ftmo_real") != "FORBIDDEN":
        raise ValueError("P2302_UNSAFE_STATE")
    if state.get("max_signal_candle") != 1:
        raise ValueError("P2302_UNSAFE_CANDLE_LIMIT")
    groups = {}
    ids = set()
    for row in rows:
        if not isinstance(row, dict) or any(row.get(k) != v for k, v in {
            "symbol":"GER40", "timeframe":"H1", "lot":"0.01",
            "mode":"PAPER_ONLY", "real_orders":"FORBIDDEN",
            "ftmo_real":"FORBIDDEN", "status":"PAPER_SIGNAL_GENERATED"}.items()):
            raise ValueError("P2302_UNSAFE_SIGNAL")
        if row.get("action") not in ("BUY","SELL") or not isinstance(row.get("candle_key"),str) or not row["candle_key"]:
            raise ValueError("P2302_INVALID_SIGNAL")
        signal_id=row.get("signal_id")
        if not isinstance(signal_id,str) or not signal_id or signal_id in ids:
            raise ValueError("P2302_DUPLICATE_ID")
        ids.add(signal_id)
        groups.setdefault((row["symbol"],row["candle_key"]),[]).append(row)
    duplicates=sum(max(0,len(v)-1) for v in groups.values())
    conflicts=sum(1 for v in groups.values() if len({r["action"] for r in v})>1)
    return {"status":"P2302_FORWARD_INVALID" if duplicates or conflicts else "PAPER_OBSERVATION_ONLY",
            "historical_signals":len(rows),"duplicate_candle_signals":duplicates,
            "conflicting_candles":conflicts,"mt5_consumption_certified":False,
            "orders_authorized":0,"e2e_certified":False,
            "requires_atomic_global_candle_lock":True}
