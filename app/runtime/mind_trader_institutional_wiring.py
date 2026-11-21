from __future__ import annotations

import ast
from pathlib import Path
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

def _inspect_source(name: str) -> dict:
    # Static AST inspection only: importing a module can execute arbitrary
    # module-level code, so discovery must not import or invoke project code.
    root = Path(__file__).resolve().parents[2]
    source = (root / (name.replace(".", "/") + ".py")).resolve()
    try:
        source.relative_to(root)
    except ValueError:
        return {"module": name, "source_ok": False, "error": "PATH_OUTSIDE_PROJECT"}
    try:
        text = source.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(source))
    except FileNotFoundError:
        return {"module": name, "source_ok": False, "error": "SOURCE_NOT_FOUND"}
    except (OSError, UnicodeError, SyntaxError) as exc:
        return {"module": name, "source_ok": False, "error": f"SOURCE_INVALID:{exc}"}
    return {
        "module": name,
        "source_ok": True,
        "classes": [n.name for n in tree.body if isinstance(n, ast.ClassDef)],
        "functions": [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and not n.name.startswith("_")],
        "import_performed": False,
        "execution_performed": False,
    }

def run_institutional_wiring(payload: dict | None = None) -> dict:
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("INVALID_PAYLOAD")
    results = [_inspect_source(name) for name in MODULES]
    source_ok = sum(row["source_ok"] for row in results)
    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "SOURCE_INSPECTION_OK_UNCERTIFIED" if source_ok == len(results) else "DEGRADED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "modules_total": len(results),
        "imports_ok": 0,
        "source_inspections_ok": source_ok,
        "runs_ok": 0,
        "execution_performed": False,
        "health_ok": 0,
        "results": results,
    }

def health() -> dict:
    results = [_inspect_source(name) for name in MODULES]
    source_ok = sum(row["source_ok"] for row in results)
    return {
        "status": "SOURCE_INSPECTION_OK_UNCERTIFIED" if source_ok == len(results) else "DEGRADED",
        "modules_total": len(results),
        "imports_ok": 0,
        "source_inspections_ok": source_ok,
        "runs_ok": 0,
        "health_ok": 0,
        "execution_performed": False,
        "results": results,
    }

def run(payload: dict | None = None) -> dict:
    return run_institutional_wiring(payload)
