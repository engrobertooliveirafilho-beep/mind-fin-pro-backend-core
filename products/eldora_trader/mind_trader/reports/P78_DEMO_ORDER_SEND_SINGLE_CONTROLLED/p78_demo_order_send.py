"""Historical P78 order-send entrypoint: permanently offline under ET665.CK.

No MetaTrader5 import, terminal connection, order_check or order_send is allowed.
The historical demo order-send behavior is intentionally not available.
"""
import json
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("reports/P78_DEMO_ORDER_SEND_SINGLE_CONTROLLED")


def run(symbol="EURUSD", lot=0.01):
    raise PermissionError("ET665_R27_MIRRORED_MT5_ORDER_SEND_FORBIDDEN")
    report = {
        "STATUS": "P78_BLOCKED_INSTITUTIONAL",
        "REASON": "ET665_CK_HISTORICAL_MT5_ORDER_SEND_DISABLED",
        "SYMBOL": str(symbol),
        "LOT": str(lot),
        "ORDER_SENT": False,
        "LIVE": "FORBIDDEN",
        "REAL_ORDERS": "FORBIDDEN",
        "FTMO_REAL": "FORBIDDEN",
        "MT5_REAL": "FORBIDDEN",
        "generated_at": datetime.now(UTC).isoformat(),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "p78_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    run()
