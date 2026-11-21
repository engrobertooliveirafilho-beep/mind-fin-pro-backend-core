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
    # Wiring is discovery-only until an execution contract is certified.
    # Importing a module never authorizes invoking its run() entry point.
    payload = payload or {}
    if not isinstance(payload, dict):
        raise ValueError('INVALID_PAYLOAD')
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

            # Execution intentionally unavailable until a verified allowlist exists.

        except Exception as e:
            row["error"] = str(e)

        results.append(row)

    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "IMPORTS_OK_UNCERTIFIED" if all(row["import_ok"] for row in results) else "DEGRADED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "modules_total": len(results),
        "imports_ok": sum(1 for r in results if r["import_ok"]),
        "runs_ok": sum(1 for r in results if r["run_ok"]),
        "execution_performed": False,
        "health_ok": sum(1 for r in results if r["health_ok"]),
        "results": results,
    }

def health() -> dict:
    # Read-only inspection: health checks must never execute module.run().
    # Importability is not proof of functional readiness.
    results = []
    for name in MODULES:
        try:
            importlib.import_module(name)
            results.append({"module": name, "import_ok": True})
        except Exception as exc:
            results.append({"module": name, "import_ok": False, "error": str(exc)})
    imports_ok = sum(row["import_ok"] for row in results)
    return {
        "status": "IMPORTS_OK_UNCERTIFIED" if imports_ok == len(MODULES) else "DEGRADED",
        "modules_total": len(MODULES),
        "imports_ok": imports_ok,
        "runs_ok": 0,
        "health_ok": 0,
        "execution_performed": False,
        "results": results,
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
