"""Historical P2302 ledger conflict detector. Audit-only; never emits orders."""
from __future__ import annotations

import csv
from collections import defaultdict
from io import StringIO

def conflicting_groups(csv_text: str) -> list[dict]:
    rows = list(csv.DictReader(StringIO(csv_text)))
    groups = defaultdict(list)
    for row in rows:
        key = tuple((row.get(k) or "").strip() for k in ("symbol", "timeframe", "candle_key"))
        if not all(key):
            raise ValueError("MISSING_CANDLE_IDENTITY")
        side = (row.get("action") or "").strip().upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("INVALID_ACTION")
        groups[key].append(row)
    conflicts = []
    for (symbol, timeframe, candle_key), candidates in sorted(groups.items()):
        actions = sorted({(r["action"] or "").strip().upper() for r in candidates})
        if len(actions) > 1:
            conflicts.append({
                "symbol": symbol, "timeframe": timeframe, "candle_key": candle_key,
                "candidate_count": len(candidates), "actions": actions,
                "emit_allowed": False, "paper_lot": 0.0,
                "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
            })
    return conflicts
