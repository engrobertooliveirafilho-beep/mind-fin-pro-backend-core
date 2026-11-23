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
    if not isinstance(payload, dict) or payload.get("mode") != "PAPER_ONLY":
        raise ValueError("PAPER_ONLY mode must be explicitly authorized before module import")
    if payload.get("real_orders") not in (None, "FORBIDDEN", False):
        raise ValueError("real orders forbidden")
    if payload.get("ftmo_real") not in (None, "FORBIDDEN", False):
        raise ValueError("FTMO real forbidden")
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

            # Child health hooks are untrusted: they may run trading code.
            # Do not invoke them during orchestration; inspection is not certification.
            row["health_inspection"] = "SKIPPED_SIDE_EFFECT_SAFETY"

            if hasattr(m, "run"):
                try:
                    import inspect
                    # Never reinterpret an arbitrary PAPER payload as positional
                    # parameters such as cycles, output_dir or broker settings.
                    signature = inspect.signature(m.run)
                    params = list(signature.parameters.values())
                    if not params or params[0].name not in ("payload", "request"):
                        row["error"] += "run_error=UNSUPPORTED_RUN_SIGNATURE;"
                        results.append(row)
                        continue
                    signature.bind(payload)
                    r = m.run(payload)
                    row["run_ok"] = (isinstance(r, dict) and r.get("ok") is True and not r.get("error") and str(r.get("status", "")).upper() not in ("FAIL", "FAILED", "ERROR", "BLOCKED", "DEGRADED", "NOT_CERTIFIED", "PENDING", "NOT_READY") or isinstance(r, dict) and str(r.get("status", "")).upper() in ("PASS", "OK", "SUCCESS", "OPERATIONAL", "PAPER_RUN_COMPLETED_UNCERTIFIED") and r.get("ok") is not False and not r.get("error"))
                    row["run_result_type"] = type(r).__name__
                    row["run_result"] = r if isinstance(r, (dict, list, str, int, float, bool)) else str(r)
                except Exception as e:
                    row["error"] += f"run_error={e};"
            else:
                row["error"] += "run_error=NO_SUPPORTED_ENTRYPOINT;"

        except Exception as e:
            row["error"] = str(e)

        results.append(row)

    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "DEGRADED" if not results or any(r["error"] or not r["run_ok"] for r in results) else "PAPER_RUN_COMPLETED_UNCERTIFIED",
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
    """Side-effect-free metadata only; never import or run trading modules."""
    return {
        "status": "UNVERIFIED",
        "modules_total": len(MODULES),
        "imports_ok": None,
        "runs_ok": None,
        "health_ok": None,
        "inspection_only": True,
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
