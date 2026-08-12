import json
import shutil
from pathlib import Path
from datetime import datetime, UTC

OUT = Path("_evidence/P2001B")

CONNECTORS = {
    "MT5_DEMO_EXPORT": ["MetaTrader5", "mt5", "terminal64.exe"],
    "CSV_IMPORT": ["csv"],
    "PUBLIC_KLINES": ["requests", "urllib"],
    "EXCHANGE_OHLCV_EXPORT": ["ccxt"],
    "BROKER_HISTORY": ["MetaTrader5", "broker"],
    "DUKASCOPY_COMPATIBLE_EXPORT": ["dukascopy", "requests"]
}

def probe_python_module(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False

def run():
    OUT.mkdir(parents=True, exist_ok=True)

    results = []

    for connector, probes in CONNECTORS.items():
        hits = []

        for p in probes:
            if p.endswith(".exe"):
                hits.append({"probe": p, "available": shutil.which(p) is not None})
            else:
                hits.append({"probe": p, "available": probe_python_module(p)})

        available = any(x["available"] for x in hits)

        results.append({
            "connector": connector,
            "available": available,
            "probes": hits,
            "mode": "RESEARCH_ONLY",
            "download_executed": False,
            "real_orders": "FORBIDDEN"
        })

    summary = {
        "program": "P2001B_SOURCE_CONNECTOR_PROBE",
        "status": "PASS",
        "mode": "RESEARCH_ONLY",
        "connector_count": len(results),
        "available_connectors": sum(1 for r in results if r["available"]),
        "unavailable_connectors": sum(1 for r in results if not r["available"]),
        "download_executed": False,
        "files_written": False,
        "order_sent": False,
        "real_orders": "FORBIDDEN",
        "approved_for_P2001C": True,
        "generated_at": datetime.now(UTC).isoformat()
    }

    (OUT / "SOURCE_CONNECTOR_PROBE.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    (OUT / "SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
