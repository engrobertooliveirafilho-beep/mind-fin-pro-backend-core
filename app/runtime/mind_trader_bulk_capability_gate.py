from __future__ import annotations

import os
from app.runtime.mind_trader_bulk_capability_wiring import run as bulk_run, health as bulk_health

def bulk_capability_gate_enabled() -> bool:
    return os.getenv("MIND_TRADER_BULK_CAPABILITY_GATE", "0") == "1"

def run_gate(payload: dict | None = None) -> dict:
    payload = payload or {}

    if not bulk_capability_gate_enabled():
        return {
            "status": "DISABLED",
            "mode": "PAPER_ONLY",
            "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN",
            "reason": "MIND_TRADER_BULK_CAPABILITY_GATE_NOT_ENABLED",
        }

    out = bulk_run(payload)

    return {
        "status": "ENABLED",
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "bulk_capabilities": out,
    }

def health() -> dict:
    base = bulk_health()
    return {
        "status": "OK",
        "gate_enabled": bulk_capability_gate_enabled(),
        "mode": "PAPER_ONLY",
        "real_orders": "FORBIDDEN",
        "ftmo_real": "FORBIDDEN",
        "bulk_modules_total": base.get("modules_total", 0),
        "bulk_imports_ok": base.get("imports_ok", 0),
        "bulk_runs_ok": base.get("runs_ok", 0),
        "bulk_health_ok": base.get("health_ok", 0),
    }
