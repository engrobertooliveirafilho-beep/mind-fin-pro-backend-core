from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone

MODULES = [
    "app.runtime.p2223_broker_emulator",
    "app.runtime.p2224_2226_institutional_core",
    "app.runtime.p2227_2229_advanced_layer",
    "app.runtime.p2131_2150_ftmo_paper_compliance_assurance",
    "app.runtime.p2081_2090_realtime_portfolio_governance",
    "app.runtime.p2091_2100_realtime_intelligence_layer",
    "app.runtime.p2071_2080_realtime_paper_runtime",
    "app.runtime.p19_governance_layer",
    "app.runtime.capability_usage_ledger",
    "app.modules.usde_core.scientific_ledger",
]

def run_institutional_wiring(payload: dict | None = None, *, execute: bool = True) -> dict:
    payload = payload or {}
    if not isinstance(payload, dict):
        return {"status": "BLOCKED", "error": "INVALID_PAYLOAD", "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}
    forbidden = {"LIVE", "REAL", "FTMO_REAL", "REAL_ORDERS"}
    if any(str(payload.get(k, "")).upper() in forbidden for k in ("mode", "execution_mode", "account_mode")) or any(payload.get(k) is True for k in ("real_orders", "live", "ftmo_real")):
        return {"status": "BLOCKED", "error": "LIVE_EXECUTION_FORBIDDEN", "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}
    results = []

    for name in MODULES:
        row = {
            "module": name,
            "import_ok": False,
            "run_ok": False,
            "health_ok": False,
            "classes": [],
            "functions": [],
            "error": "",
        }
        try:
            m = importlib.import_module(name)
            row["import_ok"] = True
            row["classes"] = [k for k, v in vars(m).items() if isinstance(v, type)]
            row["functions"] = [
                k for k, v in vars(m).items()
                if callable(v) and not isinstance(v, type) and not k.startswith("_")
            ]

            if hasattr(m, "health"):
                try:
                    h = m.health()
                    row["health_ok"] = isinstance(h, dict) and h.get("status") in ("operational", "OK", "PASS", "healthy")
                    row["health"] = h
                except Exception as e:
                    row["error"] += f"health_error={e};"

            if execute and hasattr(m, "run"):
                try:
                    signature = inspect.signature(m.run)
                    try:
                        signature.bind(payload)
                    except TypeError:
                        signature.bind()
                        r = m.run()
                    else:
                        r = m.run(payload)
                    row["run_ok"] = r is not None and not (isinstance(r, dict) and (r.get("error") or r.get("status") in ("DEGRADED", "ERROR", "FAILED", "BLOCKED")))
                    row["run_result_type"] = type(r).__name__
                    row["run_result"] = r if isinstance(r, (dict, list, str, int, float, bool)) else str(r)
                except Exception as e:
                    row["error"] += f"run_error={e};"

        except Exception as e:
            row["error"] = str(e)

        results.append(row)

    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "operational" if results and all(row["import_ok"] and (row["run_ok"] if execute else True) and row["health_ok"] and not row["error"] for row in results) else "DEGRADED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "modules_total": len(results),
        "imports_ok": sum(1 for r in results if r["import_ok"]),
        "runs_ok": sum(1 for r in results if r["run_ok"]),
        "health_ok": sum(1 for r in results if r["health_ok"]),
        "results": results,
    }

def health() -> dict:
    r = run_institutional_wiring({}, execute=False)
    return {
        "status": r["status"],
        "modules_total": r["modules_total"],
        "imports_ok": r["imports_ok"],
        "runs_ok": r["runs_ok"],
        "health_ok": r["health_ok"],
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
