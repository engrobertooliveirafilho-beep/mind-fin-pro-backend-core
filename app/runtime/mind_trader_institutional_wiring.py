from __future__ import annotations

import importlib
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

def run_institutional_wiring(payload: dict | None = None) -> dict:
    if payload is None:
        payload = {}
    if not isinstance(payload, dict) or payload.get("mode", "PAPER_ONLY") != "PAPER_ONLY" or payload.get("real_orders", "FORBIDDEN") != "FORBIDDEN" or payload.get("ftmo_real", "FORBIDDEN") != "FORBIDDEN":
        return {"program": "MIND_TRADER_INSTITUTIONAL_WIRING", "status": "BLOCKED", "reason": "PAPER_ONLY_EXECUTION_GATE", "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN", "modules_total": 0, "imports_ok": 0, "runs_ok": 0, "health_ok": 0, "results": []}
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
                    row["health_ok"] = isinstance(h, dict)
                    row["health"] = h
                except Exception as e:
                    row["error"] += f"health_error={e};"

            if hasattr(m, "run"):
                try:
                    # A TypeError inside run(payload) is a runtime failure, not
                    # evidence that run() should be invoked a second time.
                    import inspect
                    signature = inspect.signature(m.run)
                    if not signature.parameters:
                        r = m.run()
                    else:
                        r = m.run(payload)
                    row["run_ok"] = isinstance(r, dict) and str(r.get("status", "")).upper() in {"OK", "PASS", "HEALTHY", "OPERATIONAL", "SUCCESS", "COMPLETED"}
                    row["run_result_type"] = type(r).__name__
                    row["run_result"] = r if isinstance(r, (dict, list, str, int, float, bool)) else str(r)
                except Exception as e:
                    row["error"] += f"run_error={e};"

        except Exception as e:
            row["error"] = str(e)

        results.append(row)

    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "operational" if results and all(row["import_ok"] and row["run_ok"] for row in results) else "DEGRADED",
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
    # A health probe must never execute a trading motor's run() entrypoint.
    imports_ok = 0
    health_ok = 0
    for name in MODULES:
        try:
            module = importlib.import_module(name)
            imports_ok += 1
            probe = getattr(module, "health", None)
            if callable(probe):
                result = probe()
                if isinstance(result, dict) and result.get("status") in ("operational", "OK", "PASS", "HEALTHY"):
                    health_ok += 1
        except Exception:
            continue
    # Import/health probes cannot certify that any trading motor executed.
    return {
        "status": "DEGRADED",
        "modules_total": len(MODULES),
        "imports_ok": imports_ok,
        "runs_ok": 0,
        "health_ok": health_ok,
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
