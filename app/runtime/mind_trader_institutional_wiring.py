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
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("PAPER_PAYLOAD_DICT_REQUIRED")
    if payload.get("mode", "PAPER_ONLY") != "PAPER_ONLY":
        raise ValueError("PAPER_ONLY_REQUIRED")
    if payload.get("real_orders_allowed", False) is not False or payload.get("real_orders", False) not in (False, "FORBIDDEN"):
        raise ValueError("REAL_ORDERS_FORBIDDEN")
    if payload.get("ftmo_real", False) not in (False, "FORBIDDEN"):
        raise ValueError("FTMO_REAL_FORBIDDEN")
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
                    row["health_ok"] = isinstance(h, dict) and h.get("status", "operational") == "operational" and h.get("ok", True) is True
                    if not row["health_ok"]:
                        row["error"] += "health_unhealthy;"
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
                    row["run_ok"] = r is not None and not (isinstance(r, dict) and (r.get("status") not in (None, "operational", "OK", "SUCCESS") or r.get("ok") is False))
                    if not row["run_ok"]:
                        row["error"] += "run_unhealthy;"
                    row["run_result_type"] = type(r).__name__
                    row["run_result"] = r if isinstance(r, (dict, list, str, int, float, bool)) else str(r)
                except Exception as e:
                    row["error"] += f"run_error={e};"

        except Exception as e:
            row["error"] = str(e)

        results.append(row)

    return {
        "program": "MIND_TRADER_INSTITUTIONAL_WIRING",
        "status": "operational" if bool(results) and all(row["import_ok"] and not row["error"] and (row["run_ok"] if execute else row["health_ok"]) for row in results) else "DEGRADED",
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

# >>> TRADER_CANONICAL_MINIMAL_PAPER_FACTORY_R3_I_R3_R3 >>>
from dataclasses import dataclass as _trader_canonical_dataclass
from datetime import datetime as _trader_canonical_datetime
from datetime import timezone as _trader_canonical_timezone
import os as _trader_canonical_os
from typing import Any as _TraderCanonicalAny
from typing import Mapping as _TraderCanonicalMapping

from mind_trader.app.risk.ftmo_ruleset import (
    load_ftmo_config as _trader_canonical_load_ftmo_config,
)
from app.runtime.staging_v2.trader.mind_trader.app.execution.paper_broker_adapter import (
    paper_broker_summary as _trader_canonical_paper_broker_summary,
)


_TRADER_CANONICAL_REQUIRED_PAPER_ENVIRONMENT: _TraderCanonicalMapping[str, str] = {
    "TRADER_MODE": "PAPER_ONLY",
    "TRADER_LIVE": "FORBIDDEN",
    "TRADER_BROKER": "SIMULATED",
    "TRADER_NETWORK": "FORBIDDEN",
    "TRADER_ORDER_EXECUTION": "FORBIDDEN",
}


@_trader_canonical_dataclass(frozen=True, slots=True)
class PaperRuntimeComposition:
    """Immutable and inert PAPER_ONLY runtime composition."""

    mode: str
    broker_mode: str
    live_real: str
    network_access: str
    order_execution: str
    health_snapshot: _TraderCanonicalMapping[str, _TraderCanonicalAny]
    ftmo_config: _TraderCanonicalAny
    paper_broker_snapshot: _TraderCanonicalMapping[str, _TraderCanonicalAny]
    created_utc: str


def _require_paper_only_environment() -> None:
    """Reject any environment outside the certified PAPER_ONLY contract."""

    violations: list[str] = []

    for name, expected in _TRADER_CANONICAL_REQUIRED_PAPER_ENVIRONMENT.items():
        observed = _trader_canonical_os.environ.get(name)

        if observed != expected:
            violations.append(
                f"{name}={observed!r}; expected={expected!r}"
            )

    if violations:
        raise RuntimeError(
            "PAPER_ONLY environment contract rejected: "
            + " | ".join(violations)
        )


def create_paper_runtime() -> PaperRuntimeComposition:
    """
    Create one inert PAPER_ONLY composition.

    No runtime, loop, network, broker connection or order execution is started.
    """

    _require_paper_only_environment()

    health_snapshot = health()
    ftmo_config = _trader_canonical_load_ftmo_config()
    paper_broker_snapshot = _trader_canonical_paper_broker_summary()

    if not isinstance(health_snapshot, dict):
        raise TypeError("health() must return dict")

    if not isinstance(paper_broker_snapshot, dict):
        raise TypeError(
            "paper_broker_summary() must return dict"
        )

    return PaperRuntimeComposition(
        mode="PAPER_ONLY",
        broker_mode="SIMULATED",
        live_real="FORBIDDEN",
        network_access="FORBIDDEN",
        order_execution="FORBIDDEN",
        health_snapshot=health_snapshot,
        ftmo_config=ftmo_config,
        paper_broker_snapshot=paper_broker_snapshot,
        created_utc=_trader_canonical_datetime.now(
            _trader_canonical_timezone.utc
        ).isoformat(),
    )
# <<< TRADER_CANONICAL_MINIMAL_PAPER_FACTORY_R3_I_R3_R3 <<<