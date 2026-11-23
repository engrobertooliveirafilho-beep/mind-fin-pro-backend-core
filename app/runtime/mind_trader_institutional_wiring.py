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
    payload = payload or {}
    results = []

    for name in MODULES:
        row = {
            "module": name,
            "import_ok": False,
            "run_ok": False,
            "health_ok": False,
            "health_checked": False,
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
                row["health_checked"] = True
                try:
                    h = m.health()
                    row["health_ok"] = isinstance(h, dict) and str(h.get("status", "")).upper() not in {"ERROR", "FAILED", "FAIL", "DEGRADED", "BLOCKED", "NOT_IMPLEMENTED"}
                    row["health"] = h
                except Exception as e:
                    row["error"] += f"health_error={e};"

            if hasattr(m, "run") or (name == "app.runtime.p2223_broker_emulator" and hasattr(m, "run_simulation")):
                try:
                    import inspect
                    runner = m.run if hasattr(m, "run") else m.run_simulation
                    signature = inspect.signature(runner)
                    if name == "app.runtime.p2223_broker_emulator":
                        r = runner(cycles=1)
                    else:
                        try:
                            signature.bind(payload)
                        except TypeError:
                            signature.bind()
                            r = runner()
                        else:
                            r = runner(payload)
                    row["run_ok"] = r is not None and not (isinstance(r, dict) and str(r.get("status", "")).upper() in {"ERROR", "FAILED", "FAIL", "DEGRADED", "BLOCKED", "NOT_IMPLEMENTED"})
                    row["run_result_type"] = type(r).__name__
                    row["run_result"] = r if isinstance(r, (dict, list, str, int, float, bool)) else str(r)
                except Exception as e:
                    row["error"] += f"run_error={e};"

        except Exception as e:
            row["error"] = str(e)

        results.append(row)

    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "operational" if results and all(row["import_ok"] and row["run_ok"] and (not row["health_checked"] or row["health_ok"]) and not row["error"] for row in results) else "DEGRADED",
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
    r = run_institutional_wiring({})
    return {
        "status": r["status"],
        "modules_total": r["modules_total"],
        "imports_ok": r["imports_ok"],
        "runs_ok": r["runs_ok"],
        "health_ok": r["health_ok"],
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
