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

def run_institutional_wiring(payload: dict | None = None) -> dict:
    if payload is None:
        payload = {}
    elif not isinstance(payload, dict):
        raise TypeError("PAPER wiring payload must be a dictionary")
    if not MODULES:
        return {
            "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
            "status": "DEGRADED",
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN",
            "modules_total": 0,
            "imports_ok": 0,
            "runs_ok": 0,
            "health_ok": 0,
            "results": [],
        }
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
                    signature = inspect.signature(m.run)
                    parameters = list(signature.parameters.values())
                    if parameters and parameters[0].name in ("payload", "request", "context"):
                        signature.bind(payload)
                        r = m.run(payload)
                    elif not parameters:
                        r = m.run()
                    else:
                        raise TypeError("UNSUPPORTED_RUN_CONTRACT: explicit adapter required")
                    row["run_ok"] = r is not None
                    row["run_result_type"] = type(r).__name__
                    row["run_result"] = r if isinstance(r, (dict, list, str, int, float, bool)) else str(r)
                except Exception as e:
                    row["error"] += f"run_error={e};"

        except Exception as e:
            row["error"] = str(e)

        results.append(row)

    imports_ok = sum(1 for r in results if r["import_ok"])
    runs_ok = sum(1 for r in results if r["run_ok"])
    health_ok = sum(1 for r in results if r["health_ok"])
    status = "operational" if imports_ok == len(results) and runs_ok == len(results) and all(not r["error"] for r in results) else "DEGRADED"
    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "modules_total": len(results),
        "imports_ok": imports_ok,
        "runs_ok": runs_ok,
        "health_ok": health_ok,
        "results": results,
    }

def health() -> dict:
    """Non-executing module probe; never dispatch PAPER engines during health checks."""
    imports_ok = 0
    health_ok = 0
    for name in MODULES:
        try:
            module = importlib.import_module(name)
            imports_ok += 1
            probe = getattr(module, "health", None)
            if callable(probe) and isinstance(probe(), dict):
                health_ok += 1
        except Exception:
            continue
    return {
        "status": "operational" if imports_ok == len(MODULES) and health_ok == len(MODULES) and bool(MODULES) else "DEGRADED",
        "modules_total": len(MODULES),
        "imports_ok": imports_ok,
        "runs_ok": 0,
        "health_ok": health_ok,
        "execution_scope": "NON_EXECUTING_HEALTH_PROBE",
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
