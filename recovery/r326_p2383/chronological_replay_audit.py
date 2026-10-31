"""P2383 R326: deterministic chronological walk-forward on recovered P2382 rows.

Audit only: does not infer unseen candles, submit orders, or promote strategies.
"""
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

DATE_FORMAT = "%Y.%m.%d %H:%M:%S"

def audit_rows(path, windows=5):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) < windows:
        raise ValueError("INSUFFICIENT_ROWS")
    if not {"entry_time", "realized_r", "signal_id", "mode", "real_orders"}.issubset(rows[0]):
        raise ValueError("MISSING_REQUIRED_COLUMNS")
    parsed = []
    for index, row in enumerate(rows):
        if row["mode"] != "PAPER_ONLY" or row["real_orders"] != "FORBIDDEN":
            raise ValueError(f"UNSAFE_ROW_{index}")
        timestamp = datetime.strptime(row["entry_time"], DATE_FORMAT)
        realized = float(row["realized_r"])
        if not (-float("inf") < realized < float("inf")):
            raise ValueError(f"NONFINITE_R_{index}")
        parsed.append((timestamp, index, row, realized))
    parsed.sort(key=lambda item: (item[0], item[1]))
    sizes = [len(parsed) // windows + (i < len(parsed) % windows) for i in range(windows)]
    result = []
    cursor = 0
    for i, size in enumerate(sizes, 1):
        part = parsed[cursor:cursor + size]
        cursor += size
        values = [p[3] for p in part]
        result.append({"window_id": i, "start_time": part[0][0].isoformat(),
                       "end_time": part[-1][0].isoformat(), "samples": size,
                       "wins": sum(v > 0 for v in values),
                       "losses": sum(v < 0 for v in values),
                       "zero": sum(v == 0 for v in values),
                       "realized_r_sum": round(sum(values), 9)})
    repeated = sum(count - 1 for count in Counter(row["signal_id"] for _, _, row, _ in parsed).values() if count > 1)
    return {"status": "AUDIT_ONLY_NOT_OOS_CERTIFIED", "source_rows": len(parsed),
            "duplicate_signal_ids": repeated, "windows": result,
            "promotion_authorized": False, "ftmo_ready": False}
